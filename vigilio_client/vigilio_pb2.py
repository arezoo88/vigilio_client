syntax = "proto3";

package vigilio;

// Request message for returns
message GetReturnsRequest {
    string ins_code = 1;          // Optional: ETF identifier
    string seo_register_no = 2;   // Optional: Codal identifier
    string date = 3;              // Required: Date for returns
    string return_type = 4;       // Optional: return type (e.g., "pclose")
}

// Response message for returns
message GetReturnsResponse {
    repeated Return returns = 1;  // List of return objects
}

// Return message structure
message Return {
    string date = 1;
    float thirty = 2;
    float ninety = 3;
    float one_eighty = 4;
    float three_sixty = 5;
}

// The request message for getting dividends
message GetDividendsRequest {
    string ins_code = 1; // Optional: ETF identifier
    string seo_register_no = 2; // Optional: Codal identifier
}

// The response message for getting dividends
message GetDividendsResponse {
    string fund_name = 1; // Name of the fund
    repeated Dividend dividends = 2; // List of dividends
}

// The Dividend message structure
message Dividend {
    string profit_date = 1;
    int32 unit_profit = 2;  
}

// The request message for getting NAVs
message GetNavsRequest {
    string ins_code = 1; // Optional: ETF identifier
    string seo_register_no = 2; // Optional: Codal identifier
    string date = 3; // Required: Date for NAV
}

// The response message for getting NAVs
message GetNavsResponse {
    string fund_name = 1; // Name of the fund
    repeated Nav navs = 2; // List of NAVs
}

// The NAV message structure
message Nav {
    string purchase = 1; // Purchase value
    string redemption = 2; // Redemption value
    string statistical = 3; // Statistical value
}

// -----------------------------
// ShareHolder Messages
// -----------------------------
message ShareHolderSummaryRequest {
    string date = 1; // Optional filter by date
    string fund_type = 2; // Optional filter by fund type
    string search = 3; // Optional search by shareholder name
}

message ShareHolderSummary {
    int32 id = 1;
    string name = 2;
    int32 num_funds = 3;
    int64 total_share_count = 4;
    double total_value = 5;
}

message ShareHolderSummaryResponse {
    repeated ShareHolderSummary shareholders = 1;
}

message ShareHolderDetailRequest {
    string shareholder_id = 1; // ID of the shareholder
    string date = 2; // Optional: filter by specific date
    string fund_type = 3; // Optional: filter by fund type
}

message ShareHolderFundHistory {
    string fund_name = 1;
    string fund_type = 2;
    int64 share_count = 3;
    double value = 4;
    double pct_of_shares = 5;
    string date = 6;
}

message ShareHolderDetailResponse {
    string shareholder_name = 1;
    repeated ShareHolderFundHistory share_holder_histories = 2;
}

// -----------------------------
// Service definition
// -----------------------------
service VigilioService {
    rpc GetDividends(GetDividendsRequest) returns (GetDividendsResponse);
    rpc GetNavs(GetNavsRequest) returns (GetNavsResponse);
    rpc GetReturns(GetReturnsRequest) returns (GetReturnsResponse);

    // Shareholder endpoints
    rpc GetShareHolderSummary(ShareHolderSummaryRequest) returns (ShareHolderSummaryResponse);
    rpc GetShareHolderDetail(ShareHolderDetailRequest) returns (ShareHolderDetailResponse);
}
