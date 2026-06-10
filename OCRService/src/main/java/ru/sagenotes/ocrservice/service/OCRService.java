package ru.sagenotes.ocrservice.service;

import ru.sagenotes.ocrservice.dto.OCRRequestListDTO;
import ru.sagenotes.ocrservice.dto.OCRResponseDTO;
import ru.sagenotes.ocrservice.dto.OCRResponseListDTO;

public interface OCRService {

    OCRResponseListDTO process(OCRRequestListDTO dto, String userId);
    void saveOCR(String fid, String text, String noteId, String userId);
    OCRResponseListDTO getOCRbyNote(String noteId, String userId);
}
