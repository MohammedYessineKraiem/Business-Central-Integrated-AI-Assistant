codeunit 50101 "HTTP Calls"
{
    Access = Internal;

    local procedure ParseLLMResponse(JsonText: Text; var ResponseText: Text; var ModelUsed: Text; var StatusText: Text)
    var
        JsonObj: JsonObject;
        Token: JsonToken;
        JsonValue: JsonValue;
    begin
        Message('Raw JSON: %1', JsonText);
        if not JsonObj.ReadFrom(JsonText) then
            Error('Failed to parse JSON: %1', JsonText);

        if JsonObj.Get('response', Token) then begin
            JsonValue := Token.AsValue();
            ResponseText := JsonValue.AsText();
        end else
            ResponseText := 'No response';

        if JsonObj.Get('modelUsed', Token) then begin
            JsonValue := Token.AsValue();
            ModelUsed := JsonValue.AsText();
        end else
            ModelUsed := 'Unknown';

        if JsonObj.Get('status', Token) then begin
            JsonValue := Token.AsValue();
            StatusText := JsonValue.AsText();
        end else
            StatusText := 'No status';

    end;




    procedure BuildJson(prompt: Text; model: Text; context: Text): Text
    var
        JsonObj: JsonObject;
        JsonText: Text;
        JsonValue: JsonValue;
    begin
        JsonObj.Add('prompt', prompt);
        JsonObj.Add('modelName', model);
        if context <> '' then
            JsonObj.Add('context', context)
        else
            JsonObj.Add('context', '');

        JsonObj.WriteTo(JsonText);
        Message('JSON Body: %1', JsonText);
        exit(JsonText);
    end;



    procedure SendPrompt(Message: Text; ModelUsed: Text): Text
    var
        Client: HttpClient;
        Request: HttpRequestMessage;
        Response: HttpResponseMessage;
        JsonBody: Text;
        JsonResponse: Text;
        Headers: HttpHeaders;
        ResponseText: Text;
        ModelText: Text;
        ContextText: Text;
        StatusText: Text;
        ChatLog: Record "Copilot Chat Log";
        StoreInTable: Codeunit "StoreInTable";
    begin
        ContextText := StoreInTable.GetLast5ChatPrompts();
        JsonBody := BuildJson(Message, ModelUsed, ContextText);
        Request.SetRequestUri('http://localhost:5135/copilot/chat');
        Request.Method := 'POST';
        Request.Content().WriteFrom(JsonBody);
        Request.Content().GetHeaders(Headers);
        if Headers.Contains('Content-Type') then
            Headers.Remove('Content-Type');
        Headers.Add('Content-Type', 'application/json');
        if Client.Send(Request, Response) then begin
            Response.Content().ReadAs(JsonResponse);

            // Use the new procedure here to extract fields
            ParseLLMResponse(JsonResponse, ResponseText, ModelText, StatusText);
            Message('Prompt: %1\Response: %2\Model: %3\Context: %4\Status: %5', Message, ResponseText, ModelUsed, ContextText, StatusText);

            // Store the response in the chat log
            StoreInTable.HandlePromptResponse(Message, ResponseText, ModelText, ContextText, StatusText, ChatLog."PromptType"::Question);

            exit(ResponseText);
        end else
            Error('Failed to contact backend.');
    end;




}
