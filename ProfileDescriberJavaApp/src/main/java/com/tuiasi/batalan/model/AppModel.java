package com.tuiasi.batalan.model;

import com.google.api.services.drive.model.File;
import com.tuiasi.batalan.model.data.QuestionModel;
import lombok.Getter;

import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.security.GeneralSecurityException;

@Getter
public class AppModel {
    private final GoogleDrive googleDriveApiService;
    private File profileDriveReference;
    private BufferedImage bufferedImage;
    private QuestionModel[] questionModels;

    public AppModel(GoogleDrive googleDriveApiService) throws GeneralSecurityException, IOException {
        this.googleDriveApiService = new GoogleDrive();
    }

    public void setNewRandomProfile() {
        try {
            this.profileDriveReference = googleDriveApiService.getRandomImageFile();

            // Download the random image.
            try (ByteArrayOutputStream imageOutputStream = googleDriveApiService.downloadImage(this.profileDriveReference)) {
                // Update imagePanel component with image data.
                byte[] data = imageOutputStream.toByteArray();
                ByteArrayInputStream inputStream = new ByteArrayInputStream(data);

                this.bufferedImage = ImageIO.read(inputStream);
            }

            // Get the attributes. TODO: This is mocked.
            // TODO: Get attributes from MongoDB.
            this.questionModels = new QuestionModel[]{
                    QuestionModel.builder()
                            .withName("Blond hair?")
                            .withAnswers(new String[] {"Yes"})
                            .build(),
                    QuestionModel.builder()
                            .withName("Face mark?")
                            .withAnswers(new String[] {"No"})
                            .build(),
                    QuestionModel.builder()
                            .withName("Pointy chin?")
                            .withAnswers(new String[] {"Yes", "No"})
                            .build()
            };
        } catch (IOException e) {
            System.out.println("Warning: Could not set new profile: " + e.getMessage());
        }
    }

    public void updateQuestion(QuestionModel updatedQuestionModel) {
        // TODO: Questions can be a hash map to improve this operation.
        for (QuestionModel questionModel : this.questionModels) {
            if (questionModel.getName().equals(updatedQuestionModel.getName())) {
                updatedQuestionModel.setAnswers(updatedQuestionModel.getAnswers());
            }
        }
    }


    public void setBufferedImage(BufferedImage bufferedImage) {
        this.bufferedImage = bufferedImage;
    }

    public void setProfileDriveReference(File profileDriveReference) {
        this.profileDriveReference = profileDriveReference;
    }

    public void setQuestionModels(QuestionModel[] questionModels) {
        this.questionModels = questionModels;
    }
}
