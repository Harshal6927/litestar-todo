# LiteStar TODO app

A simple todo app built with LiteStar framework.

## Local Setup

> This project uses Python `3.12.x`

> Refer to `.env.example` file to create a `.env` file

### With Virutal Environment

#### Clone this repo and open the folder in your terminal, then run the below to commands to create a virtual environment.

Note: This commands are for Windows, for other OS, please refer to the [official documentation](https://docs.python.org/3/library/venv.html) for creating a virtual environment.

```bash
py -m venv venv
```

Activate virutal environment

```bash
.\venv\Scripts\activate
```

Change directory to the project folder

```bash
cd litestar-todo
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the project

```bash
litestar run
```

Now visit `localhost:8000`

Note: You can see OpenAPI docs at `localhost:8000/schema` and Swagger UI at `localhost:8000/schema/swagger`
