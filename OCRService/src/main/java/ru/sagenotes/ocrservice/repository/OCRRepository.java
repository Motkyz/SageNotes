package ru.sagenotes.ocrservice.repository;

import org.springframework.data.repository.CrudRepository;
import ru.sagenotes.ocrservice.model.OCRModel;

import java.util.UUID;

public interface OCRRepository extends CrudRepository<OCRModel, UUID> {
}
