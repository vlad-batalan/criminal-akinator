package com.tuiasi.batalan.view;

import javax.swing.*;
import java.awt.*;
import java.awt.image.BufferedImage;

public class ProfilePanel extends JPanel {
    private final CriminalImagePanel criminalImagePanel;
    public ProfilePanel() {
        super();
        // Instructions label is a static component.
        JLabel instructionsLabel = new JLabel("<html>" +
                                              "<p>Instructions:</p>" +
                                              "<p>Look at the image and provide the best answers that describe the person from image.</p>" +
                                              "</html>", SwingConstants.CENTER);
        this.criminalImagePanel = new CriminalImagePanel();


        this.setLayout(new BoxLayout(this, BoxLayout.PAGE_AXIS));
        this.add(instructionsLabel, BorderLayout.PAGE_START);
        this.add(criminalImagePanel, BorderLayout.SOUTH);
        this.setVisible(true);
    }

    public void setProfileImage(BufferedImage image) {
        this.criminalImagePanel.changeBufferedImage(image);
    }
}
