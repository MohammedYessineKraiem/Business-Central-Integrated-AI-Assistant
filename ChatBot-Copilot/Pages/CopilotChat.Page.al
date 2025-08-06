page 50102 "CopilotChat"
{
    PageType = Card;
    Caption = 'Copilot Chat';
    UsageCategory = Administration;
    ApplicationArea = All;
    SourceTable = "Copilot Chat Log";
    Editable = true;
    layout
    {
        area(Content)
        {
            group("User Input")
            {
                field(Message; Rec.Message)
                {
                    ApplicationArea = All;
                    MultiLine = true;
                    ToolTip = 'Enter your message to the Copilot.';
                }
                field("ModelUsed"; Rec."ModelUsed")
                {
                    ApplicationArea = All;
                    ToolTip = 'Select which AI model to use.';
                }
            }

            group("Copilot Response")
            {
                field(Response; Rec.Response)
                {
                    ApplicationArea = All;
                    MultiLine = true;
                    Editable = false;
                    ToolTip = 'Response from the Copilot.';
                }
                field("Times-tamp"; Rec."Times-tamp")
                {
                    ApplicationArea = All;
                    Editable = false;
                    ToolTip = 'When the message was sent.';
                }
            }
        }
    }


    actions
    {
        area(processing)
        {
            action(SendMessage)
            {
                Caption = '📤 Send Message';
                ApplicationArea = All;

                trigger OnAction()
                var
                    HttpCallsCodeunit: Codeunit "HTTP Calls";
                    ResponseText: Text;
                begin
                    if Rec.Message = '' then
                        Error('Please enter a message.');

                    ResponseText := HttpCallsCodeunit.SendPrompt(Rec.Message, Format(Rec."ModelUsed"));

                    Rec.Response := ResponseText;
                    Rec."Times-tamp" := CurrentDateTime();
                    Rec.Modify(true);
                    CurrPage.Update(false);

                    Message('Message sent and stored.');
                end;
            }

            action(ResetInput)
            {
                Caption = '🧹 Clear Message';
                ApplicationArea = All;

                trigger OnAction()
                begin
                    Rec.Message := '';
                    Rec.Modify(true);
                    CurrPage.Update(false);
                end;
            }
        }
    }

    trigger OnOpenPage()
    var
        ChatLog: Record "Copilot Chat Log";
    begin
        if Rec.IsEmpty() then begin
            ChatLog.Init();
            ChatLog.Insert();
            Rec := ChatLog;
        end;
    end;

}
