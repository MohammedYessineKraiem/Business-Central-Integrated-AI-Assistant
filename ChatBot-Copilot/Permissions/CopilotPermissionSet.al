PermissionSet 50103 "CopilotPermSet"
{
    Assignable = true;
    Caption = 'Copilot Permission Set';
    Permissions = tabledata "Copilot Chat Log" = RIMD,
                  page "CopilotChat" = X,
                  codeunit "HTTP Calls" = X;
    //later to add more permissions
}