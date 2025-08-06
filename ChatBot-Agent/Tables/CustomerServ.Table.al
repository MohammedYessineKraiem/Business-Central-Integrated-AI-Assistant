table 50120 "CustomerService"
{
    Caption = 'Customer Service';
    DataClassification = CustomerContent;

    fields
    {
        field(1; "Customer ID"; Code[20])
        {
            DataClassification = CustomerContent;
            Caption = 'Customer ID';
        }

        field(2; "Full Name"; Text[100])
        {
            DataClassification = CustomerContent;
            Caption = 'Full Name';
        }

        field(3; "Username"; Text[50])
        {
            DataClassification = CustomerContent;
            Caption = 'Username';
        }

        field(4; "Email"; Text[100])
        {
            DataClassification = CustomerContent;
            Caption = 'Email';
        }

        field(5; "Phone Number"; Text[30])
        {
            DataClassification = CustomerContent;
            Caption = 'Phone Number';
        }

        field(6; "Created At"; DateTime)
        {
            DataClassification = SystemMetadata;
            Caption = 'Created At';
        }
    }

    keys
    {
        key(PK; "Customer ID") { Clustered = true; }
    }
}
