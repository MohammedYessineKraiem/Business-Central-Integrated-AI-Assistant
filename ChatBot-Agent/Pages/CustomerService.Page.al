page 50124 "Customer Service List"
{
    PageType = List;
    SourceTable = "CustomerService";
    ApplicationArea = All;
    UsageCategory = Lists;
    Caption = 'Customer Service';

    layout
    {
        area(content)
        {
            repeater(Group)
            {
                field("Customer ID"; Rec."Customer ID") { }
                field("Full Name"; Rec."Full Name") { }
                field("Username"; Rec.Username) { }
                field("Email"; Rec.Email) { }
                field("Phone Number"; Rec."Phone Number") { }
                field("Created At"; Rec."Created At") { }
            }
        }
    }
}
