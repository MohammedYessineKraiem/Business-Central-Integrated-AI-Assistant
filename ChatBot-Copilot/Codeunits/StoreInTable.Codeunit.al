codeunit 50100 StoreInTable
{

    Subtype = Normal;
    Access = Internal;

    procedure GetLast5ChatPrompts(): Text
    var
        ChatLogRec: Record "Copilot Chat Log";
        PromptTypeFilter: Option;
        TextAccumulator: Text;
        Counter: Integer;
    begin
        PromptTypeFilter := ChatLogRec."PromptType"::Question;

        if ChatLogRec.FindSet(true) then begin
            // Move to the last record
            while ChatLogRec.Next() <> 0 do;
            repeat
                if ChatLogRec."PromptType" = PromptTypeFilter then begin
                    Counter += 1;
                    TextAccumulator += 'User Asked ' + ChatLogRec."Message" + ' Your Response Was ' + ChatLogRec."Response" + '\n';
                end;
            until (Counter = 5) or (ChatLogRec.Next(-1) = 0);
        end;

        exit(TextAccumulator);
    end;


    procedure ConvertTextToAIModelEnum(ModelName: Text): Enum "AI Model"
    var
        ModelEnum: Enum "AI Model";
    begin
        case ModelName.ToLower() of
            'gpt-3.5-turbo':
                ModelEnum := ModelEnum::GPT35Turbo;
            'claude-3':
                ModelEnum := ModelEnum::Claude3;
            'mistral-7b':
                ModelEnum := ModelEnum::Mistral7B;
            'together-ai':
                ModelEnum := ModelEnum::TogetherAI;
            'groq':
                ModelEnum := ModelEnum::Groq;
        end;

        exit(ModelEnum);
    end;

    procedure TruncateStringIfNeeded(Source: Text; MaxLen: Integer): Text;
    begin
        if StrLen(Source) > MaxLen then
            exit(CopyStr(Source, 1, MaxLen))
        else
            exit(Source);
    end;

    procedure TruncateContext(Context: Text; MaxLen: Integer): Text;
    begin
        if StrLen(Context) > MaxLen then
            exit(CopyStr(Context, StrLen(Context) - MaxLen + 1, MaxLen))  // last part for context
        else
            exit(Context);
    end;

    procedure HandlePromptResponse(Prompt: Text; Response: Text; Model: Text; Context: Text; Status: Text; PromptTypeText: Option)
    var
        ChatLog: Record "Copilot Chat Log";
    begin
        Prompt := TruncateStringIfNeeded(Prompt, 2048);
        Response := TruncateStringIfNeeded(Response, 2048);
        Context := TruncateContext(Context, 2048);
        ChatLog.Init();
        ChatLog."Message" := Prompt;
        ChatLog."Response" := Response;
        ChatLog."ModelUsed" := ConvertTextToAIModelEnum(Model);
        ChatLog."Context" := Context;
        ChatLog."Status" := Status;
        ChatLog."Times-tamp" := CurrentDateTime();
        ChatLog."PromptType" := PromptTypeText;
        ChatLog.Insert();
        Message('Saved chat with status ' + Status);
    end;

}



