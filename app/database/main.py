from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def main() -> bool:
    return True


if __name__ == "__main__":
    main()
