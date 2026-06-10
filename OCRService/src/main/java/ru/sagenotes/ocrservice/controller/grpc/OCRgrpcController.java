package ru.sagenotes.ocrservice.controller.grpc;

import io.grpc.Status;
import io.grpc.stub.StreamObserver;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import net.devh.boot.grpc.server.service.GrpcService;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.access.prepost.PreAuthorize; // Добавлено
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.server.ResponseStatusException;
import org.springframework.security.core.Authentication;
import ru.sagenotes.ocrservice.dto.OCRRequestDTO;
import ru.sagenotes.ocrservice.dto.OCRRequestListDTO;
import ru.sagenotes.ocrservice.dto.OCRResponseListDTO;
import ru.sagenotes.ocrservice.grpc.*;
import ru.sagenotes.ocrservice.service.OCRService;

import java.util.List;

@GrpcService
@RequiredArgsConstructor
@Slf4j
public class OCRgrpcController extends OcrGrpcServiceGrpc.OcrGrpcServiceImplBase {

    private final OCRService ocrService;

    @Override
    @PreAuthorize("isAuthenticated()")
    public void getOcrByNote(OcrByNoteRequest request, StreamObserver<OcrResponseList> responseObserver) {
        try {
            Authentication authentication =
                    SecurityContextHolder.getContext().getAuthentication();

            if (authentication == null || !(authentication.getPrincipal() instanceof Jwt jwt)) {
                throw new AccessDeniedException("Пользователь не аутентифицирован или токен невалиден");
            }

            String userId = jwt.getClaim("sub");

            OCRResponseListDTO dto = ocrService.getOCRbyNote(request.getNoteId(), userId);

            mapFiles(responseObserver, dto);

        } catch (ResponseStatusException e) {
            log.error("Заметка не найдена: {}", e.getMessage());
            responseObserver.onError(Status.NOT_FOUND
                    .withDescription(e.getReason())
                    .asRuntimeException());
        } catch (AccessDeniedException e) {
            log.error("Ошибка доступа: {}", e.getMessage());
            responseObserver.onError(Status.PERMISSION_DENIED
                    .withDescription(e.getMessage())
                    .asRuntimeException());
        } catch (Exception e) {
            log.error("Системная ошибка в gRPC методе", e);
            responseObserver.onError(Status.INTERNAL
                    .withDescription("Внутренняя ошибка сервера")
                    .asRuntimeException());
        }
    }

    @Override
    @PreAuthorize("isAuthenticated()")
    public void processOcr(ProcessOcrRequest request, StreamObserver<OcrResponseList> responseObserver) {
        try {
            Authentication authentication =
                    SecurityContextHolder.getContext().getAuthentication();

            if (authentication == null || !(authentication.getPrincipal() instanceof Jwt jwt)) {
                throw new AccessDeniedException("Пользователь не аутентифицирован или токен невалиден");
            }

            String userId = jwt.getClaim("sub");

            List<OCRRequestDTO> serviceFiles = request.getFilesList().stream()
                    .map(grpcFile -> new OCRRequestDTO(
                            grpcFile.getFid(),
                            grpcFile.getFileUrl()
                    ))
                    .toList();

            OCRRequestListDTO requestDto = new OCRRequestListDTO(request.getNoteId(), serviceFiles);

            OCRResponseListDTO responseDto = ocrService.process(requestDto, userId);

            mapFiles(responseObserver, responseDto);

        } catch (AccessDeniedException e) {
            log.error("Ошибка доступа при обработке OCR: {}", e.getMessage());
            responseObserver.onError(Status.PERMISSION_DENIED
                    .withDescription(e.getMessage())
                    .asRuntimeException());
        } catch (Exception e) {
            log.error("Системная ошибка при обработке OCR", e);
            responseObserver.onError(Status.INTERNAL
                    .withDescription("Ошибка сервера при распознавании текста")
                    .asRuntimeException());
        }
    }

    private void mapFiles(StreamObserver<OcrResponseList> responseObserver, OCRResponseListDTO responseDto) {
        List<OcrFileResponse> grpcFiles = responseDto.getFiles().stream()
                .map(fileDto -> OcrFileResponse.newBuilder()
                        .setFid(fileDto.getFid())
                        .setText(fileDto.getText() != null ? fileDto.getText() : "")
                        .build())
                .toList();

        OcrResponseList response = OcrResponseList.newBuilder()
                .setNoteId(responseDto.getNoteId())
                .addAllFiles(grpcFiles)
                .build();

        responseObserver.onNext(response);
        responseObserver.onCompleted();
    }
}