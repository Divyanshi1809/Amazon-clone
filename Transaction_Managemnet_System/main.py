import random
import logging

logging.basicConfig(
    filename="transaction.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

#Custom Context manager
class FileManager:
    def __init__(self, filename, mode):
        self.filename = filename
        self.mode = mode
        self.file = None

    def __enter__(self):
        logging.info(f"Opening file: {self.filename}")
        self.file = open(self.filename, self.mode)
        return self.file

    def __exit__(self, exc_type, exc_value, traceback):
        self.file.close()
        logging.info(f"Closing file: {self.filename}")
        return False

class TransactionManager:
    def __init__(self, filename, initial_balance=1000):
        self.filename = filename
        self.balance = initial_balance
        self.transaction_id = 1

  
    def generate_transactions(self, count):
        with FileManager(self.filename, "w") as file:
            for _ in range(count):
                txn_type = random.choice(["CREDIT", "DEBIT"])

                if txn_type == "DEBIT" and self.balance == 0:
                    txn_type = "CREDIT"

                if txn_type == "CREDIT":
                    amount = random.randint(100, 500)
                    self.balance += amount
                else:
                    amount = random.randint(1, self.balance)
                    self.balance -= amount

                record = f"{self.transaction_id},{txn_type},{amount},{self.balance}\n"
                file.write(record)

                self.transaction_id += 1

    
    def read_transactions(self):
        with FileManager(self.filename, "r") as file:
            for line in file:
                try:
                    tid, ttype, amount, balance = line.strip().split(",")
                    yield {
                        "id": int(tid),
                        "type": ttype,
                        "amount": int(amount),
                        "balance": int(balance)
                    }
                except Exception as e:
                    logging.error(f"Invalid record skipped: {line.strip()}")

   
    def process_transactions(self):
        total_txns = 0
        total_credit = 0
        total_debit = 0
        final_balance = 0

        for txn in self.read_transactions():
            total_txns += 1

            if txn["type"] == "CREDIT":
                total_credit += txn["amount"]
            elif txn["type"] == "DEBIT":
                total_debit += txn["amount"]

            final_balance = txn["balance"]

        return {
            "Total Transactions": total_txns,
            "Total Credit": total_credit,
            "Total Debit": total_debit,
            "Final Balance": final_balance
        }



if __name__ == "__main__":
    manager = TransactionManager("transactions.txt", 1000)

    manager.generate_transactions(20)

    summary = manager.process_transactions()

    for key, value in summary.items():
        print(f"{key}: {value}")
