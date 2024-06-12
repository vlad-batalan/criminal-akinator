package com.tuiasi.batalan.view;

import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionListener;

public class AttributesPanel extends JPanel {
    private final JTextField newQuestionTextField;
    private final JButton newQuestionButton;
    private final JButton completeDescriptionButton;
    private final JLabel newQuestionErrorLabel;
    private final JButton randomProfileButton;
    private final JButton notDescribedProfileButton;

    public AttributesPanel() {
        super();
        this.setLayout(new GridLayout(3, 1));//new BoxLayout(this, BoxLayout.Y_AXIS));

        // Add describe text field label.
        JPanel newQuestionPanel = new JPanel();
        JLabel describeTextFieldLabel = new JLabel("<html><p>If a feature is not in the list</p>" +
                                                   "<p>You can add it yourself.</p>" +
                                                   "<p>Try to be simple and also make sure to link the concept to the body part.</p>" +
                                                   "<p>Examples: Curly hair, Long nose, Pointed chin, Red hair</p>" +
                                                   "</html>");

        // Add text field for new attributes.
        this.newQuestionTextField = new JTextField(30);
        newQuestionTextField.setMaximumSize(
                newQuestionTextField.getPreferredSize());

        // Add a button for submitting a new attribute.
        this.newQuestionButton = new JButton("Submit new question");

        // Initially invisible.
        this.newQuestionErrorLabel = new JLabel();
        this.newQuestionErrorLabel.setForeground(Color.RED);
        this.newQuestionErrorLabel.setVisible(false);

        newQuestionPanel.setLayout(new BoxLayout(newQuestionPanel, BoxLayout.Y_AXIS));
        newQuestionPanel.add(describeTextFieldLabel);
        newQuestionPanel.add(this.newQuestionTextField);
        newQuestionPanel.add(this.newQuestionButton);
        newQuestionPanel.add(this.newQuestionErrorLabel);

        // Add label description before the new profiles/
        JPanel changeProfilePanel = new JPanel();
        JLabel changeProfileDescription = new JLabel("<html><p>Change the current profile to another</p>" +
                                                     "<p>Be careful, answers for the current one will be lost.</p></html>");
        this.randomProfileButton = new JButton("Change to random profile");
        this.notDescribedProfileButton = new JButton("Change to new profile");

        changeProfilePanel.setLayout(new BoxLayout(changeProfilePanel, BoxLayout.Y_AXIS));
        changeProfilePanel.add(changeProfileDescription);
        changeProfilePanel.add(this.randomProfileButton);
        changeProfilePanel.add(this.notDescribedProfileButton);

        // Add label.
        JPanel completeDescriptionPanel = new JPanel();
        JLabel completeDescription = new JLabel("Press only when you are sure that description is complete.");

        // Add a button for completing a profile description.
        this.completeDescriptionButton = new JButton("Complete the profile description");

        completeDescriptionPanel.setLayout(new BoxLayout(completeDescriptionPanel, BoxLayout.Y_AXIS));
        completeDescriptionPanel.add(completeDescription);
        completeDescriptionPanel.add(this.completeDescriptionButton);

        this.add(newQuestionPanel);
        this.add(changeProfilePanel);
        this.add(completeDescriptionPanel);
//        this.add(this.newQuestionButton);
//
//        this.add(changeProfileDescription);
//        this.add(randomProfileButton);
//        this.add(notDescribedProfileButton);
//
//        this.add(completeDescription);
//        this.add(this.completeDescriptionButton);
    }

    public void toggleNewQuestionError(String message, boolean isVisible) {
        this.newQuestionErrorLabel.setText(message);
        this.newQuestionErrorLabel.setVisible(isVisible);
        this.validate();
    }

    public void completeDescription(ActionListener listener) {
        this.completeDescriptionButton.addActionListener(listener);
    }

    public void submitQuestion(ActionListener listener) {
        this.newQuestionButton.addActionListener(listener);
    }

    public String getNewQuestionText() {
        return this.newQuestionTextField.getText();
    }

    public void onChangeToRandomProfile(ActionListener e) {
        this.randomProfileButton.addActionListener(e);
    }

    public void onNotDescribedProfileButton(ActionListener e) {
        this.notDescribedProfileButton.addActionListener(e);
    }
}
