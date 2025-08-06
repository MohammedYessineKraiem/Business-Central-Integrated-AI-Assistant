table 50121 "CopilotEntity"
{
    Caption = 'Copilot Entity';
    DataClassification = ToBeClassified;

    fields
    {
        field(1; "Entity ID"; Code[20])
        {
            Caption = 'Entity ID';
            DataClassification = SystemMetadata;
        }

        field(2; "Customer ID"; Code[20])
        {
            Caption = 'Customer ID';
            DataClassification = CustomerContent;
        }

        field(3; "Title"; Text[100])
        {
            Caption = 'Title';
            DataClassification = CustomerContent;
        }

        field(4; "Description"; Text[250])
        {
            Caption = 'Description';
            DataClassification = CustomerContent;
        }

        field(5; "Status"; Option)
        {
            OptionMembers = Open,InProgress,Completed,Cancelled;
            Caption = 'Status';
            DataClassification = CustomerContent;
        }

        field(6; "Created At"; DateTime)
        {
            Caption = 'Created At';
            DataClassification = SystemMetadata;
        }
    }

    keys
    {
        key(PK; "Entity ID") { Clustered = true; }
    }

    fieldgroups
    {
        fieldgroup(DropDown; "Entity ID", "Title", "Status")
        {
        }
    }
}
