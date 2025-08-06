page 50100 "Copilot Chat Log List"
{
    PageType = List;
    SourceTable = "Copilot Chat Log";
    ApplicationArea = All;
    InsertAllowed = true;
    UsageCategory = Lists;
    Caption = 'Copilot Chat Log';

    layout
    {
        area(content)
        {
            repeater(Group)
            {
                field("Log ID"; 'Log_ID') { }

                field("PromptType"; 'PromptType') { }

                field("Message"; 'Message') { }

                field("Response"; 'Response') { }

                field("ModelUsed"; 'ModelUsed') { }

                field("Context"; 'Context') { }

                field("Status"; 'Status') { }

                field("Times-tamp"; 'Times-tamp') { }
            }
        }
    }
}
