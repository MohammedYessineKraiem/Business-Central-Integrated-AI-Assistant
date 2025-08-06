page 50103 "Copilot Agent"
{
    PageType = Card;
    Caption = 'Copilot Agent';
    UsageCategory = Administration;
    ApplicationArea = All;
    SourceTable = "Copilot Chat Log";
    Editable = true;

    layout
    {
        area(Content)
        {
            group("Agent Command Input")
            {
                field(Message; Rec.Message)
                {
                    ApplicationArea = All;
                    MultiLine = true;
                    ToolTip = 'Type a natural language command (e.g., "create a customer named Mark in Paris").';
                }
                field("ModelUsed"; Rec."ModelUsed")
                {
                    ApplicationArea = All;
                    ToolTip = 'Choose which AI model to use (e.g., OpenAI, LocalLLM).';
                }
            }

            group("Agent Response Output")
            {
                field(Response; Rec.Response)
                {
                    ApplicationArea = All;
                    MultiLine = true;
                    Editable = false;
                    ToolTip = 'LLM-generated execution result or error message.';
                }
                field(Status; Rec.Status)
                {
                    ApplicationArea = All;
                    Editable = false;
                    ToolTip = 'Was the command executed successfully?';
                }
                field("Times-tamp"; Rec."Times-tamp")
                {
                    ApplicationArea = All;
                    Editable = false;
                    ToolTip = 'When the command was executed.';
                }
            }
        }
    }

    actions
    {
        area(processing)
        {
            action(SendCommand)
            {
                Caption = '⚙️ Execute Command';
                ApplicationArea = All;

                trigger OnAction()
                var
                    CmdSender: Codeunit "AgentCommandSender";
                    ResultText: Text;
                    StatusText: Text;
                begin
                    if Rec.Message = '' then
                        Error('Please enter a command.');


                    ResultText := CmdSender.SendCommand(Rec.Message, Format(Rec."ModelUsed"), StatusText);


                    // Fill response fields
                    Rec.Response := ResultText;
                    Rec.Status := StatusText;
                    Rec."Times-tamp" := CurrentDateTime();
                    Rec."PromptType" := Rec."PromptType"::Command;

                    Rec.Modify(true);
                    CurrPage.Update(false);
                    Message('Command executed and logged.');
                end;
            }

            action(ClearInputs)
            {
                Caption = '🧹 Clear Fields';
                ApplicationArea = All;

                trigger OnAction()
                begin
                    Rec.Message := '';
                    Rec.Response := '';
                    Rec.Status := '';
                    Rec.Modify(true);
                    CurrPage.Update(false);
                end;
            }
        }
    }

    trigger OnOpenPage()
    var
        Log: Record "Copilot Chat Log";
    begin
        if Rec.IsEmpty() then begin
            Log.Init();
            Log.Insert();
            Rec := Log;
        end;
    end;
}
