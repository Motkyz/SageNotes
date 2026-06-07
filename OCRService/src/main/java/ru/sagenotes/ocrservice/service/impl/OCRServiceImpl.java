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
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.GetObjectRequest;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

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
                String extractedText = processFile(file);
                OCRResponseDTO resp = new OCRResponseDTO(fid, extractedText);

                saveOCR(fid, extractedText, noteId);

                files.add(resp);
            } catch (Exception e) {
                log.error("Ошибка при обработке файла в OCR сервисе: {}", e.getMessage(), e);
            }
        }

        return new OCRResponseListDTO(noteId, files);
    }

    public String processFile(File tempFile) {
        if (tempFile == null || !tempFile.exists()) {
            return null;
        }

        try {
            String originalFilename = tempFile.getName();

            String suffix = ".tmp";
            if (originalFilename.contains(".")) {
                suffix = originalFilename.substring(originalFilename.lastIndexOf("."));
            }

            OCRProcessor ocrProcessor = new OCRProcessor();
            String extractedText;

            if (suffix.equalsIgnoreCase(".pdf")) {
                log.info("Запуск PDF OCR");
                extractedText = ocrProcessor.extractTextFromPdf(tempFile);
            } else {
                log.info("Запуск Image OCR");
                extractedText = ocrProcessor.extractTextFromImage(tempFile);
            }

            tempFile.delete();

            return extractedText;

        } catch (Exception e) {
            log.error("Ошибка при обработке файла в OCR сервисе: {}", e.getMessage(), e);
        }

        return null;
    }

    @Override
    public void saveOCR(String fid, String text, String noteId) {
        OCRModel ocrModel = new OCRModel(fid, text, noteId);
        repository.save(ocrModel);
    }

    @Override
    public OCRResponseDTO getOCR(String fid) {
        Optional<OCRModel> model = repository.findById(fid);

        return model.map(ocrModel -> new OCRResponseDTO(ocrModel.getFid(), ocrModel.getText())).orElse(null);
    }

    private File downloadFromS3(String fileId) throws IOException {
        try {
            GetObjectRequest getRequest = GetObjectRequest.builder()
                    .bucket(bucketName)
                    .key(fileId)
                    .build();

            Path tempFile = Files.createTempFile("ocr_download_", ".tmp");

            s3Client.getObject(getRequest, tempFile);

            return tempFile.toFile();

        } catch (Exception e) {
            log.error("Failed to download file from S3: {}", fileId, e);
            throw new IOException("S3 download failed", e);
        }
    }
}
