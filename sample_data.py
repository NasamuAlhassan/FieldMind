from database import get_stats, init_db, save_report
from extractor import extract_field_report
from rag import add_report_to_rag

SAMPLE_REPORTS = [
    "My name be Kwame in Accra. Madam Efua complain say the new carton price too high pass last month.",
    "I am Akosua at Kumasi. Client Kofi still waiting for goods three days now, delivery truck delayed.",
    "Na Sule from Tamale. Alhaji Musa happy well well, product move fast and he ask for more stock next week.",
    "This is Yaw in Tema. Auntie Mansa says warehouse stock finish and customers are leaving.",
    "Abena from Takoradi here. Road to client shop bad, our van no fit pass quick, delivery slowing business.",
    "Me I be Kojo for Bolgatanga. Client Saaka dey vex because invoice payment still not reflecting after transfer.",
    "Aisha reporting from Wa. Competitor drop price hard and our client Karim threatening to switch supplier.",
    "This is Kwaku in Sunyani. All good today, Madam Adwoa praised service and paid on time.",
    "I am Sena at Ho. Shop owner Yvette says she received wrong item size, she sounds frustrated.",
    "Bismark in Techiman. Customer Nana requests urgent restock before market day or sales go spoil.",
    "Esi from Accra. Client Kojo says our team handled replacement quickly, very positive feedback.",
    "Rahim at Kumasi. Delivery bike break down so package for Mr. Boateng late again.",
    "Adjei in Tamale. Market women complain price argument every day, they say we must renegotiate.",
    "Priscilla from Tema. Major client Richmond happy with promo campaign, wants bigger order next cycle.",
    "Haruna in Takoradi. Heavy rain cut road, two shops no receive stock and owners are angry now.",
]


def load_sample_data() -> None:
    init_db()
    current = get_stats()
    if current.get("total", 0) > 0:
        print("Database already has data. Skipping sample load to avoid duplicates.")
        return

    total = len(SAMPLE_REPORTS)
    print(f"Loading {total} sample reports...")
    for index, report in enumerate(SAMPLE_REPORTS, start=1):
        try:
            extracted = extract_field_report(report)
            report_id = save_report(extracted)
            add_report_to_rag(str(report_id), extracted.get("summary", ""), extracted)
            print(f"[{index}/{total}] Loaded report ID {report_id}")
        except Exception as error:
            print(f"[{index}/{total}] Failed: {error}")

    print("Sample data load completed.")


if __name__ == "__main__":
    load_sample_data()
