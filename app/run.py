import uvicorn

if __name__ == '__main__':
    uvicorn.run(
        "main:create_app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config="./logging.yaml"
    )
