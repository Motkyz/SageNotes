package ru.sagenotes.ocrservice.repository;

import org.springframework.data.repository.CrudRepository;
import ru.sagenotes.ocrservice.model.NoteModel;

import java.util.UUID;

public interface NoteRepository extends CrudRepository<NoteModel, UUID> {
}
