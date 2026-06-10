package ru.sagenotes.ocrservice.service.impl;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;
import ru.sagenotes.ocrservice.dto.OCRRequestDTO;
import ru.sagenotes.ocrservice.dto.OCRRequestListDTO;
import ru.sagenotes.ocrservice.dto.OCRResponseDTO;
import ru.sagenotes.ocrservice.dto.OCRResponseListDTO;
import ru.sagenotes.ocrservice.model.NoteModel;
import ru.sagenotes.ocrservice.model.OCRModel;
import ru.sagenotes.ocrservice.repository.NoteRepository;
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
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
public class OCRServiceImpl implements OCRService {

    private final NoteRepository noteRepository;
    private final S3Client s3Client;

    @Value("${s3.bucket.name}")
    private String bucketName;

    @Override
    @Transactional
    public OCRResponseListDTO process(OCRRequestListDTO dto, String userId) {
        String noteId = dto.getNoteId();
        List<OCRResponseDTO> files = new ArrayList<>();

        for (OCRRequestDTO fileInfo : dto.getFiles()) {
            File file = null;
            try {
                String fid = fileInfo.getFid();
                String url = fileInfo.getFileUrl();

                file = downloadFromS3(url);

                String extractedText = processFile(file, url);
                OCRResponseDTO resp = new OCRResponseDTO(fid, extractedText);

                saveOCR(fid, extractedText, noteId, userId);
                files.add(resp);
            } catch (Exception e) {
                log.error("Ошибка при обработке файла в OCR сервисе: {}", e.getMessage(), e);
            } finally {
                if (file != null && file.exists()) {
                    boolean deleted = file.delete();
                    log.debug("Временный файл удален в finally: {}", deleted);
                }
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
    @Transactional
    public void saveOCR(String fid, String text, String noteId, String userId) {

        NoteModel noteModel = noteRepository.findById(UUID.fromString(noteId))
                .orElseGet(() -> new NoteModel(
                        UUID.fromString(noteId),
                        UUID.fromString(userId),
                        new ArrayList<>()));

        OCRModel ocrModel = new OCRModel(
                UUID.fromString(fid),
                text,
                noteModel
        );

        noteModel.addOCR(ocrModel);
        noteRepository.save(noteModel);
    }

    @Override
    @Transactional(readOnly = true)
    public OCRResponseListDTO getOCRbyNote(String noteId, String userId) {

        NoteModel noteModel = noteRepository.findById(UUID.fromString(noteId))
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Note not found"));

        if (!noteModel.getOwnerId().equals(UUID.fromString(userId))) {
            throw new AccessDeniedException("Пользователь не владелец заметки");
        }

        List<OCRResponseDTO> files = noteModel.getOcrs().stream()
                .map(ocrModel -> new OCRResponseDTO(ocrModel.getFid().toString(), ocrModel.getText()))
                .toList();

        return new OCRResponseListDTO(noteId, files);
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