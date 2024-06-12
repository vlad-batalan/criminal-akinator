package com.tuiasi.batalan.view;

import javax.swing.*;
import java.awt.*;
import java.awt.image.BufferedImage;

public class CriminalImagePanel extends JPanel {
    private BufferedImage image;
    public void changeBufferedImage(BufferedImage image) {
        this.image = image;
        this.repaint();
    }

    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
        if (image != null) {
            setPreferredSize(new Dimension(image.getWidth(), image.getHeight()));
            Dimension resizedDims = getResizedImageDimensions();
            g.drawImage(image, 0, 0, resizedDims.width, resizedDims.height, this);
        }
    }

    private Dimension getResizedImageDimensions() {
        float widthHeightRatio = image.getWidth() / (float) image.getHeight();
        int scaledHeight = (int) (this.getWidth() / widthHeightRatio);
        return new Dimension(this.getWidth(), scaledHeight);
    }
}
