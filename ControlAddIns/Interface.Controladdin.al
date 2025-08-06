controladdin "Copilot Chat"
{
    Scripts = 'ControlAddins/xpilot.js';
    StartupScript = 'ControlAddins/xpilot.js';
    StyleSheets = 'ControlAddins/xpilotStyle.css';

    RequestedHeight = 1000;
    RequestedWidth = 1500;

    MinimumHeight = 600;
    MinimumWidth = 800;


    event SendPrompt(PromptText: Text; ModelName: Text);
    event SendCommand(PromptText: Text; ModelName: Text);
    event SendClassification(Message: Text; ModelName: Text);
    procedure ReceiveALResponse(ResponseText: Text);



}
