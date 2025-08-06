/*
You can show past chats to the user (like a chat window).

You can reconstruct context for better LLM replies (e.g. send last 3 messages as context).

You can fine-tune prompts based on what worked well.

You can audit/debug what users asked and how the bot replied.

You can track feedback, such as user thumbs up/down.
*/

table 50101 "Copilot Chat Log"
{
    Caption = 'Copilot Chat Log';
    DataClassification = ToBeClassified;


    fields
    {
        field(1; "Log ID"; Integer)
        {
            DataClassification = CustomerContent;
            Caption = 'Log ID';
            AutoIncrement = true;
            Editable = false;
        }
        field(2; "Message"; Text[2000])
        {
            DataClassification = CustomerContent;
            Caption = 'Message';
        }
        field(3; "Response"; Text[2048])
        {
            DataClassification = CustomerContent;
            Caption = 'Response';
        }

        field(4; "ModelUsed"; Enum "AI Model")
        {
            DataClassification = CustomerContent;
            Caption = 'Model Used';
            ToolTip = 'The AI model used for generating the response.';
        }
        field(5; "Context"; Text[2048])
        {
            DataClassification = CustomerContent;
            Caption = 'Context';
            ToolTip = 'Additional context provided for the chat.';
        }
        field(6; "Status"; Text[30])
        {
            DataClassification = CustomerContent;
            Caption = 'Status';
        }
        field(7; "Times-tamp"; DateTime)
        {
            DataClassification = CustomerContent;
            Caption = 'Timestamp';
            Editable = false;
        }
        field(8; "PromptType"; Option)
        {
            OptionMembers = Question,Command;
            DataClassification = ToBeClassified;
        }
    }

    keys
    {
        key(PK; "Log ID")
        {
            Clustered = true;
        }
        key(TimeKey; "Times-tamp") { }
    }

}
