page 50115 "Copilot Chat Launcher"
{
    layout
    {
        area(content)
        {
            usercontrol(CopilotChat; "Copilot Chat")
            {
                ApplicationArea = All;



                trigger SendPrompt(PromptText: Text; ModelName: Text)
                var
                    Handler: Codeunit "http Calls";
                    Result: Text;

                begin
                    Result := Handler.SendPrompt(PromptText, ModelName);


                    CurrPage.CopilotChat.ReceiveALResponse(Result)
                end;

                trigger SendCommand(PromptText: Text; ModelName: Text)
                var
                    Handler: Codeunit "AgentCommandSender";
                    Result: Text;
                    Status: Text;
                begin
                    Result := Handler.SendCommand(PromptText, ModelName, Status);
                    CurrPage.CopilotChat.ReceiveALResponse(Result);
                end;

                trigger SendClassification(Message: Text; ModelName: Text)
                var
                    Handler: Codeunit "UnifiedClassifierHTTP";
                    Classification: Text;
                begin
                    Classification := Handler.ClassifyPrompt(Message, ModelName);
                    CurrPage.CopilotChat.ReceiveALResponse(Classification);
                end;



            }
        }
    }


}
