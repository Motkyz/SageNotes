package ru.sagenotes.ocrservice.controller.restful;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;
import ru.sagenotes.ocrservice.dto.OCRRequestListDTO;
import ru.sagenotes.ocrservice.dto.OCRResponseListDTO;
import ru.sagenotes.ocrservice.service.OCRService;

@RestController
@RequiredArgsConstructor
@RequestMapping("/ocr")
@Validated
public class OCRController {

    private final OCRService ocrService;

    @PostMapping("/upload")
    public OCRResponseListDTO processFiles(
            @Valid @RequestBody OCRRequestListDTO dto,
            @AuthenticationPrincipal Jwt jwt) {
        return ocrService.process(dto, jwt.getClaim("sub"));
    }

    @GetMapping("/note/{note_id}")
    public OCRResponseListDTO getOCRbyNote(
            @PathVariable @NotBlank String note_id,
            @AuthenticationPrincipal Jwt jwt) {
        return ocrService.getOCRbyNote(note_id, jwt.getClaim("sub"));
    }
}