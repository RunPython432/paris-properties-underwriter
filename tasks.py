import datetime
from REAItools import (
    PropertyDeal,
    StrategyType,
    underwrite_deal_with_ai,
    stessa_generate_financial_insights,
    dscr_lender_estimate_refi,
)

# In the future this will call PropStream/Reonomy etc.
def daily_scan_deals():
    print("=== Daily Scan –", datetime.date.today(), "===")

    # For now, simulate 2 deals in your Charlotte buy box
    sample_deals = [
        PropertyDeal(
            address="Triplex A",
            city="Gastonia",
            state="NC",
            zip_code="28052",
            bedrooms=6,
            bathrooms=3.0,
            units=3,
            year_built=1985,
            purchase_price=350000,
            projected_rent_roll={"Unit1": 1250, "Unit2": 1250, "Unit3": 1200},
            strategy=StrategyType.BRRRR,
        ),
        PropertyDeal(
            address="Quad B",
            city="Rock Hill",
            state="SC",
            zip_code="29730",
            bedrooms=8,
            bathrooms=4.0,
            units=4,
            year_built=1990,
            purchase_price=480000,
            projected_rent_roll={
                "Unit1": 1300,
                "Unit2": 1300,
                "Unit3": 1300,
                "Unit4": 1300,
            },
            strategy=StrategyType.BRRRR,
        ),
    ]

    for deal in sample_deals:
        bundle = underwrite_deal_with_ai(deal, photos=["photo1.jpg"])
        uw = bundle["underwriting"]
        print(f"- {deal.address}: DSCR={uw.dscr:.2f}, CoC={uw.cash_on_cash:.2%}, Good={uw.is_good_deal}")


def quarterly_refi_check():
    print("=== Quarterly Refi Check –", datetime.date.today(), "===")

    # In real life you'd load actual portfolio; here we simulate one
    portfolio = [
        PropertyDeal(
            address="123 Sample Triplex",
            city="Gastonia",
            state="NC",
            zip_code="28052",
            bedrooms=6,
            bathrooms=3.0,
            units=3,
            year_built=1985,
            purchase_price=375000,
            projected_rent_roll={"Unit1": 1300, "Unit2": 1300, "Unit3": 1250},
            strategy=StrategyType.BRRRR,
        )
    ]

    stessa_data = stessa_generate_financial_insights()
    portfolio_noi = stessa_data.get("portfolio_noi", 0)

    for deal in portfolio:
        noi_estimate = portfolio_noi / max(len(portfolio), 1)
        refi = dscr_lender_estimate_refi(deal, noi_estimate)
        print(f"- {deal.address}: LTV={refi.ltv_after_refi:.2f}, DSCR={refi.dscr_after_refi:.2f}, Recommend={refi.recommend_refi}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 tasks.py [daily-scan | quarterly-refi]")
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "daily-scan":
        daily_scan_deals()
    elif cmd == "quarterly-refi":
        quarterly_refi_check()
    else:
        print("Unknown command. Use: daily-scan or quarterly-refi")
