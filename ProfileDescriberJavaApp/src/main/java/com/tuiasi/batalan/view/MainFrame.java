package com.tuiasi.batalan.view;

import com.tuiasi.batalan.controller.AppController;

import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.JSplitPane;
import java.awt.GridLayout;

public class MainFrame extends JFrame {
    private final ProfilePanel profilePanel;
    private final QuestionsPanel questionsPanel;
    private final AttributesPanel attributesPanel;

    public MainFrame() {
        super("Describe profiles application");
        this.setLocationRelativeTo(null);
        this.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        this.setSize(1000, 500);

        // Create main components:
        // - Left component with image.
        this.profilePanel = new ProfilePanel();

        // - Middle component with questions.
        this.questionsPanel = new QuestionsPanel();

        // - Right component with new attributes and form submission.
        this.attributesPanel = new AttributesPanel();

        // Middle and Right components are linked by an intermediate component with grid layout.
        JPanel questionsAttributesPanel = new JPanel(new GridLayout(1, 2, 3, 3));
        questionsAttributesPanel.add(this.questionsPanel);
        questionsAttributesPanel.add(this.attributesPanel);

        // Split the left section and the center-right ones.
        JSplitPane leftCenterSplitPlane = new JSplitPane(JSplitPane.HORIZONTAL_SPLIT, this.profilePanel, questionsAttributesPanel);
        leftCenterSplitPlane.setResizeWeight(0.5);
        leftCenterSplitPlane.setOneTouchExpandable(false);
        leftCenterSplitPlane.setContinuousLayout(true);
        this.add(leftCenterSplitPlane);

        AppController applicationController = new AppController(this.profilePanel, this.questionsPanel, this.attributesPanel);

        // Make frame visible.
        this.setVisible(true);
    }
}
