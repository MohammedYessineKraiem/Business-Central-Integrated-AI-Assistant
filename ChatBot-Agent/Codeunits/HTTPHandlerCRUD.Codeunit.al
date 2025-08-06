codeunit 50113 "AgentCommandSender"
{
    Access = Internal;

    local procedure ParseCommandResponse(JsonText: Text; var ResponseText: Text; var StatusText: Text; var DataText: Text)

    var
        JsonObj: JsonObject;
        Token: JsonToken;
        JsonValue: JsonValue;
    begin
        Message('Raw Command JSON: %1', JsonText);

        if not JsonObj.ReadFrom(JsonText) then
            Error('Failed to parse command response: %1', JsonText);

        if JsonObj.Get('message', Token) then
            ResponseText := Token.AsValue().AsText()
        else
            ResponseText := 'No response';
        if JsonObj.Get('success', Token) then
            StatusText := Token.AsValue().AsText()
        else
            StatusText := 'No status';
        if JsonObj.Get('data', Token) then begin
            if Token.IsValue then
                DataText := Token.AsValue().AsText()
            else begin
                Token.WriteTo(DataText); // Safe and works for both objects and arrays
            end;
        end else
            DataText := '{}';

    end;


    procedure BuildCommandJson(Prompt: Text; Model: Text): Text
    var
        JsonObj: JsonObject;
        JsonText: Text;
    begin
        JsonObj.Add('prompt', Prompt);
        JsonObj.Add('Model', Model);
        JsonObj.WriteTo(JsonText);
        Message('Command JSON Body: %1', JsonText);
        exit(JsonText);
    end;


    procedure SendCommand(Prompt: Text; ModelUsed: Text; var Status: Text): Text
    var
        Client: HttpClient;
        Request: HttpRequestMessage;
        Response: HttpResponseMessage;
        JsonBody: Text;
        JsonResponse: Text;
        Headers: HttpHeaders;
        ResponseText: Text;
        DataText: Text;
        ContextText: Text;
        CombinedText: Text;
        ChatLog: Record "Copilot Chat Log";
        StoreInTable: Codeunit "StoreInTable";
    begin
        JsonBody := BuildCommandJson(Prompt, ModelUsed);
        Request.SetRequestUri('http://localhost:5135/copilot/command');
        Request.Method := 'POST';
        Request.Content().WriteFrom(JsonBody);
        Request.Content().GetHeaders(Headers);
        if Headers.Contains('Content-Type') then
            Headers.Remove('Content-Type');

        Headers.Add('Content-Type', 'application/json');
        ContextText := 'CONFIDENTIAL: This is a test command sent to the backend service.';
        if Client.Send(Request, Response) then begin
            Response.Content().ReadAs(JsonResponse);

            // Parse response
            ParseCommandResponse(JsonResponse, ResponseText, Status, DataText);

            // Store in shared log table
            StoreInTable.HandlePromptResponse(Prompt, ResponseText, ModelUsed, ContextText, Status, ChatLog."PromptType"::Command);
            CombinedText := StrSubstNo('%1   --->   Data:  --->   %2', ResponseText, DataText);

            exit(CombinedText);
        end else
            Error('Failed to reach backend /copilot/command.');
    end;


}
