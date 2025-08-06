page 50121 "Copilot Entity List"
{
    PageType = List;
    SourceTable = "CopilotEntity";
    ApplicationArea = All;
    UsageCategory = Lists;
    Caption = 'Copilot Entity';

    layout
    {
        area(content)
        {
            repeater(Group)
            {
                field("Entity ID"; Rec."Entity ID") { }
                field("Customer ID"; Rec."Customer ID") { }
                field("Title"; Rec.Title) { }
                field("Description"; Rec.Description) { }
                field("Status"; Rec.Status) { }
                field("Created At"; Rec."Created At") { }
            }
        }
    }
}
