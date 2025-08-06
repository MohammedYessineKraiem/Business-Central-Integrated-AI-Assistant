codeunit 50102 "UnifiedClassifierHTTP"
{
    Access = Internal;

    local procedure ParseLLmClassification(JsonText: Text; var Classification: Text)
    var
        JsonObj: JsonObject;
        Token: JsonToken;
        JsonValue: JsonValue;
    begin
        if not JsonObj.ReadFrom(JsonText) then
            Error('Failed to parse JSON: %1', JsonText);

        if JsonObj.Get('type', Token) then begin
            JsonValue := Token.AsValue();
            Classification := JsonValue.AsText();
        end else
            Classification := 'Unknown';
    end;

    procedure ClassifyPrompt(Message: Text; ModelUsed: Text): Text
    var
        Client: HttpClient;
        Request: HttpRequestMessage;
        Response: HttpResponseMessage;
        JsonBody: Text;
        JsonResponse: Text;
        Headers: HttpHeaders;
        Classification: Text;
        JsonObj: JsonObject;
        Token: JsonToken;
    begin
        JsonBody := BuildJson(Message, ModelUsed);

        Request.SetRequestUri('http://localhost:5135/copilot/unified');
        Request.Method := 'POST';
        Request.Content().WriteFrom(JsonBody);
        Request.Content().GetHeaders(Headers);
        if Headers.Contains('Content-Type') then
            Headers.Remove('Content-Type');
        Headers.Add('Content-Type', 'application/json');

        if Client.Send(Request, Response) then begin
            Response.Content().ReadAs(JsonResponse);

            ParseLLmClassification(JsonResponse, Classification);

            exit(Classification);
        end else
            Error('❌ Failed to contact unified classification endpoint.');
    end;

    local procedure BuildJson(prompt: Text; model: Text): Text
    var
        JsonObj: JsonObject;
        JsonText: Text;
    begin
        JsonObj.Add('prompt', prompt);
        JsonObj.Add('modelName', model);
        JsonObj.WriteTo(JsonText);
        exit(JsonText);
    end;
}

