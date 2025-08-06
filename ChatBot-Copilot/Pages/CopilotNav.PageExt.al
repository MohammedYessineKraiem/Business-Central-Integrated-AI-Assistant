pageextension 50102 "XPilotDropDown" extends "Business Manager Role Center"
{
    actions
    {
        addlast(Sections)
        {
            group(XPilotMenu)
            {
                Caption = 'XPilot Tools';

                action("XPilot Chat")
                {
                    ApplicationArea = All;
                    Caption = 'Chat XPilot';
                    ToolTip = 'Open the XPilot chat page.';
                    RunObject = Page "CopilotChat";
                }
                action("XPilot Agents")
                {
                    ApplicationArea = All;
                    Caption = 'XPilot Agents';
                    ToolTip = 'Manage your XPilot agents.';
                    RunObject = Page "Copilot Agent";
                }

                action("Insights Dashboard And Predictions")
                {
                    ApplicationArea = All;
                    Caption = 'Insights And AI Suggestion';
                    ToolTip = 'View your XPilot-generated insights.';
                    RunObject = Page "Rag Chat Page";
                }
                action("XPilot Chat Ad")
                {
                    ApplicationArea = All;
                    Caption = 'XPilot Chat Advanced';
                    ToolTip = 'Open the XPilot assistant window.';
                    RunObject = Page "Copilot Chat Launcher";
                }



            }
        }
    }
}
