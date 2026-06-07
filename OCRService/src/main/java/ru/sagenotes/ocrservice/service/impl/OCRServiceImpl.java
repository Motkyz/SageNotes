package ru.sagenotes.ocrservice.service.impl;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import ru.sagenotes.ocrservice.dto.OCRRequestDTO;
import ru.sagenotes.ocrservice.dto.OCRRequestListDTO;
import ru.sagenotes.ocrservice.dto.OCRResponseDTO;
import ru.sagenotes.ocrservice.dto.OCRResponseListDTO;
import ru.sagenotes.ocrservice.model.OCRModel;
import ru.sagenotes.ocrservice.repository.OCRRepository;
import ru.sagenotes.ocrservice.service.OCRService;
import ru.sagenotes.ocrservice.util.OCRProcessor;
import software.amazon.awssdk.core.sync.ResponseTransformer;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.GetObjectRequest;
import software.amazon.awssdk.services.s3.model.S3Exception;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
public class OCRServiceImpl implements OCRService {

    private final OCRRepository repository;
    private final S3Client s3Client;

    @Value("${s3.bucket.name}")
    private String bucketName;

    @Override
    public OCRResponseListDTO process(OCRRequestListDTO dto) {
        String noteId = dto.getNoteId();
        List<OCRResponseDTO> files = new ArrayList<>();

        for (OCRRequestDTO fileInfo : dto.getFiles()) {
            try {
                String fid = fileInfo.getFid();
                String url = fileInfo.getFileUrl();

                File file = downloadFromS3(url);

                String extractedText = processFile(file, url);
                OCRResponseDTO resp = new OCRResponseDTO(fid, extractedText);

                saveOCR(fid, extractedText, noteId);
                files.add(resp);
            } catch (Exception e) {
                log.error("Ошибка при обработке файла в OCR сервисе: {}", e.getMessage(), e);
            }
        }

        return new OCRResponseListDTO(noteId, files);
    }

    public String processFile(File tempFile, String originalUrl) {
        if (tempFile == null || !tempFile.exists()) {
            return null;
        }

        try {
            String lowerUrl = originalUrl.toLowerCase();
            boolean isPdf = lowerUrl.contains(".pdf");

            OCRProcessor ocrProcessor = new OCRProcessor();
            String extractedText;

            if (isPdf) {
                log.info("Запуск PDF OCR для файла: {}", tempFile.getName());
                extractedText = ocrProcessor.extractTextFromPdf(tempFile);
            } else {
                log.info("Запуск Image OCR для файла: {}", tempFile.getName());
                extractedText = ocrProcessor.extractTextFromImage(tempFile);
            }

            if (tempFile.exists()) {
                boolean deleted = tempFile.delete();
                log.debug("Временный файл удален: {}", deleted);
            }

            return extractedText;

        } catch (Exception e) {
            log.error("Ошибка при обработке файла в OCR сервисе: {}", e.getMessage(), e);
        }

        return null;
    }

    @Override
    public void saveOCR(String fid, String text, String noteId) {
        OCRModel ocrModel = new OCRModel(UUID.fromString(fid), text, UUID.fromString(noteId));
        repository.save(ocrModel);
    }

    @Override
    public OCRResponseDTO getOCR(String fid) {
        Optional<OCRModel> model = repository.findById(UUID.fromString(fid));
        return model.map(ocrModel -> new OCRResponseDTO(ocrModel.getFid().toString(), ocrModel.getText())).orElse(null);
    }

    private File downloadFromS3(String fileUrl) throws IOException {
        try {
            java.net.URI uri = java.net.URI.create(fileUrl);
            String path = uri.getPath();

            String cleanPath = path.substring(1);
            String s3Key = cleanPath.substring(cleanPath.indexOf("/") + 1);

            GetObjectRequest getRequest = GetObjectRequest.builder()
                    .bucket(bucketName)
                    .key(s3Key)
                    .build();

            Path tempFilePath = Files.createTempFile("ocr_", ".tmp");

            Files.deleteIfExists(tempFilePath);

            s3Client.getObject(getRequest, ResponseTransformer.toFile(tempFilePath));

            if (!Files.exists(tempFilePath) || Files.size(tempFilePath) == 0) {
                throw new IOException("Скачанный файл пуст или не существует");
            }

            return tempFilePath.toFile();

        } catch (S3Exception e) {
            log.error("Ошибка S3 при скачивании файла. Статус: {}, Ошибка: {}",
                    e.statusCode(), e.awsErrorDetails().errorMessage(), e);
            throw new IOException("Ошибка при загрузке из S3: " + e.awsErrorDetails().errorMessage(), e);
        } catch (IOException e) {
            log.error("IO-ошибка при загрузке: {}", e.getMessage(), e);
            throw e;
        } catch (Exception e) {
            log.error("Ошибка при загрузке файле", e);
            throw new IOException("Ошибка при загрузке из S3", e);
        }
    }
}