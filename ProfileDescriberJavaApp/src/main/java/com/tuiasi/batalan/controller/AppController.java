package com.tuiasi.batalan.controller;

import com.google.api.services.drive.model.File;
import com.tuiasi.batalan.model.GoogleDrive;
import com.tuiasi.batalan.model.MetadataStorage;
import com.tuiasi.batalan.model.data.QuestionAnswerModel;
import com.tuiasi.batalan.model.data.QuestionModel;
import com.tuiasi.batalan.view.AttributesPanel;
import com.tuiasi.batalan.view.ProfilePanel;
import com.tuiasi.batalan.view.QuestionsPanel;
import org.bson.Document;

import javax.imageio.ImageIO;
import javax.swing.*;
import java.awt.image.BufferedImage;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.security.GeneralSecurityException;
import java.util.*;

import static com.tuiasi.batalan.configs.DriveConstants.PROFILES_TOTAL_NUMBER;
import static com.tuiasi.batalan.configs.MongoConstants.KNOWLEDGE_COLLECTION;

public class AppController {
    private final ProfilePanel profilePanel;
    private final AttributesPanel attributesPanel;
    private final QuestionsPanel questionsPanel;
    private final GoogleDrive googleDrive;
    private final MetadataStorage metadataStorage;
    private QuestionAnswerModel questionModel;
    private File profileDriveFile;
    private BufferedImage profileImage;

    public AppController(ProfilePanel profilePanel, QuestionsPanel questionsPanel, AttributesPanel attributesPanel) {
        try {
            this.googleDrive = new GoogleDrive();
        } catch (IOException | GeneralSecurityException e) {
            throw new RuntimeException("Could not initialise Google Drive", e);
        }

        metadataStorage = new MetadataStorage();

        // Initialize all sub-components.
        this.profilePanel = profilePanel;
        this.attributesPanel = attributesPanel;
        this.questionsPanel = questionsPanel;

        // Filter questions functionality.
        this.questionsPanel.onFilterQuestionsClick(e -> {
            String filterQuery = this.questionsPanel.getFilterQuery();
            syncQuestionModelAnswers();

            boolean hasChanged = false;
            if (filterQuery.isBlank()) {
                // Make all the queries visible.
                for (QuestionModel question : this.questionModel.getQuestionMap().values()) {
                    if (!question.isVisible()) {
                        hasChanged = true;
                        question.setVisible(true);
                    }
                }
            } else {
                filterQuery = filterQuery.toLowerCase(Locale.ROOT);

                // Filter questions.
                for (QuestionModel question : this.questionModel.getQuestionMap().values()) {
                    String lowerCaseQuery = question.getName().toLowerCase(Locale.ROOT);
                    if (lowerCaseQuery.contains(filterQuery)) {
                        if (!question.isVisible()) {
                            hasChanged = true;
                            question.setVisible(true);
                        }
                    } else {
                        if (question.isVisible()) {
                            hasChanged = true;
                            question.setVisible(false);
                        }
                    }
                }
            }

            // Update the view if queries have changed.
            if (hasChanged) {
                this.questionsPanel.updateQuestions(this.questionModel);
            }
        });

        // Submit new question functionality.
        this.attributesPanel.submitQuestion(e -> {
            // Question to submit.
            String question = this.attributesPanel.getNewQuestionText();

            // Check cases when is empty.
            if (question.isBlank()) {
                this.attributesPanel.toggleNewQuestionError("Question must not be empty!", true);
                return;
            }

            int dialogResult = JOptionPane.showConfirmDialog(null,
                    "<html><p>Are you sure you want to submit this question?</p>" +
                    "<p>Make sure you respect a format similar to other questions.</p>",
                    null, JOptionPane.YES_NO_OPTION);
            if(dialogResult == JOptionPane.NO_OPTION) {
                return;
            }

            // Upload question to MongoDB.
            boolean isSuccessful = this.metadataStorage.insertQuestion(question);

            if (!isSuccessful) {
                this.attributesPanel.toggleNewQuestionError("Something went wrong with storing the question.", true);
                return;
            }

            // No error here.
            this.attributesPanel.toggleNewQuestionError(null, false);

            // Upload questionModel with the new question.
            this.questionModel.getQuestionMap().put(question, QuestionModel.builder()
                    .withName(question)
                    .withAnswers(new String[]{})
                    .withIsVisible(true)
                    .build());

            // Upload the questionView.
            // - sync the questions.
            this.syncQuestionModelAnswers();

            // - use updateQuestion.
            this.questionsPanel.updateQuestions(this.questionModel);
        });

        // Change to random profile.
        this.attributesPanel.onChangeToRandomProfile(e -> {
            changeProfile(true);
        });

        // Change to new profile.
        this.attributesPanel.onNotDescribedProfileButton(e -> {
            changeProfile(false);
        });

        // On document complete.
        this.attributesPanel.completeDescription(e -> {
            int dialogResult = JOptionPane.showConfirmDialog(null,
                    "<html><p>Are you sure you want to submit the description?</p>" +
                    "<p>Saving incomplete descriptions could impact the integrity of the dataset!</p>",
                    null, JOptionPane.YES_NO_OPTION);
            if(dialogResult == JOptionPane.NO_OPTION) {
                return;
            }

            // Sync question answers.
            this.syncQuestionModelAnswers();

            // Filter questions based on number of answers
            List<String> twoAnswerQuestions = new ArrayList<>();

            // A base document is formed by appending all one answer questions.
            Document baseDocument = new Document();
            baseDocument.put(this.metadataStorage.getTargetField(), this.profileDriveFile.getName());

            for (QuestionModel question : this.questionModel.getQuestionMap().values()) {
                if (question.getAnswers().length == 1) {
                    baseDocument.put(question.getName(), question.getAnswers()[0]);
                } else if (question.getAnswers().length == 2) {
                    twoAnswerQuestions.add(question.getName());
                }
            }

            // Create document based on questions answered.
            // - One answer -> Normal save.
            // - Two answers -> Backtracking save.
            // - No answer -> Omit attribute.
            List<Document> insertList = buildDocuments(baseDocument, twoAnswerQuestions);

            // Save all documents to mongo.
            metadataStorage.saveToCollection(insertList, KNOWLEDGE_COLLECTION);

            // Change profile.
            changeProfile(false);
            this.profilePanel.validate();
        });

        // Initialize the first state.
        changeProfile(true);
    }

    private List<Document> buildDocuments(Document baseDocument, List<String> twoAnswerQuestion) {
        List<Document> result = new ArrayList<>();

        // Check out the edge cases.
        if (twoAnswerQuestion.isEmpty()) {
            Document copyDocument = Document.parse(baseDocument.toJson());
            result.add(copyDocument);
            return result;
        }

        // Pick up the first question and treat both Yes and No cases.
        String questionName = twoAnswerQuestion.get(0);
        List<String> remainingQuestions = twoAnswerQuestion.subList(1, twoAnswerQuestion.size());

        // Yes branch.
        baseDocument.append(questionName, "Yes");
        result.addAll(buildDocuments(baseDocument, remainingQuestions));

        // No branch.
        baseDocument.append(questionName, "No");
        result.addAll(buildDocuments(baseDocument, remainingQuestions));

        // Clean.
        baseDocument.remove(questionName);
        return result;
    }

    private void changeProfile(boolean isRandomProfile) {
        if (isRandomProfile) {
            this.profileImage = this.loadRandomProfile();
        } else {
            Set<Integer> existingProfiles = this.metadataStorage.selectDistinctProfiles();

            // Choose the lowest number not in existing profiles.
            Integer nextProfileId = null;
            for (int i = 0; i <= PROFILES_TOTAL_NUMBER; i++) {
                if (!existingProfiles.contains(i)) {
                    nextProfileId = i;
                    break;
                }
            }

            if (nextProfileId == null) {
                this.profileImage = this.loadRandomProfile();
            } else {
                this.profileImage = this.loadSpecificProfile(nextProfileId);
            }
        }
        this.questionModel = this.loadQuestions();

        this.profilePanel.setProfileImage(profileImage);
        this.questionsPanel.updateQuestions(questionModel);
    }

    private BufferedImage loadSpecificProfile(Integer profileId) {
        try {
            // Get a new image from drive.
            this.profileDriveFile = googleDrive.searchImageFile(profileId);
            return driveFileToImage(this.profileDriveFile);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    private BufferedImage loadRandomProfile() {
        try {
            // Get a new image from drive.
            this.profileDriveFile = googleDrive.getRandomImageFile();
            return driveFileToImage(this.profileDriveFile);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    private BufferedImage driveFileToImage(File driveFile) {
        try {
            // Download the random image.
            try (ByteArrayOutputStream imageOutputStream = googleDrive.downloadImage(driveFile)) {
                // Update imagePanel component with image data.
                byte[] data = imageOutputStream.toByteArray();
                ByteArrayInputStream inputStream = new ByteArrayInputStream(data);

                return ImageIO.read(inputStream);
            }
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }


    private QuestionAnswerModel loadQuestions() {
        Map<String, QuestionModel> questionModelMap = new HashMap<>();
        List<String> questions = this.metadataStorage.getQuestions();

        // For each question, create Model object.
        for (String questionName : questions) {
            questionModelMap.put(questionName, QuestionModel.builder()
                    .withAnswers(new String[]{})
                    .withIsVisible(true)
                    .withName(questionName)
                    .build());
        }

        return QuestionAnswerModel.builder()
                .withQuestionMap(questionModelMap)
                .build();

        // Pass the questions to questionPanel view.
    }

    private void syncQuestionModelAnswers() {
        Map<String, QuestionModel> viewState = this.questionsPanel.getQuestions();
        for (Map.Entry<String, QuestionModel> entry : viewState.entrySet()) {
            // Update the answer in the model.
            // TODO: Is there any possibility that there are extra questions in the inner state.
            QuestionModel modelValue = this.questionModel.getQuestionMap().get(entry.getKey());
            modelValue.setAnswers(entry.getValue().getAnswers());
        }
    }
}
