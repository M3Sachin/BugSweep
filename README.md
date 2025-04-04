# DevInspector

**DevInspector** is an AI-based code review tool that helps developers ensure high-quality and maintainable code. Powered by cutting-edge AI models, **DevInspector** analyzes your code for common errors, bugs, style violations, and best practices. This tool is designed to automate code review processes, saving developers valuable time while improving the overall quality of their code.

While **DevInspector** is powered by the **Gemini API** and model, it is highly customizable, and you can easily switch to any other AI model of your choice.

---

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Setting Up GitHub App with Repository Permissions](#setting-up-github-app-with-repository-permissions)
- [Testing Locally with ngrok](#testing-locally-with-ngrok)
- [Contributing](#contributing)
- [License](#license)

---

## Introduction

DevInspector leverages artificial intelligence to automatically review code against predefined standards and rules. It provides valuable feedback, identifies potential bugs, and suggests improvements, helping developers write cleaner, more efficient code.

The tool uses the **Gemini API** and model by default for code analysis, but you can easily configure it to work with any AI model of your choice, making it versatile and adaptable to your needs.

---

## Features

- **Automatic Code Review on Commit**: DevInspector automatically reviews your code each time you make a commit, ensuring that code quality is maintained consistently.
- **AI-Powered Code Review**: Uses advanced AI to automatically review code and suggest improvements.
- **Customizable Models**: While the tool uses the **Gemini API** by default, you can switch to any model that fits your needs.
- **Error Detection**: Identifies common errors and potential bugs in your codebase.
- **Code Quality Insights**: Provides actionable insights and suggestions for improving code quality.
- **Integration with Git**: Seamlessly integrates with your Git workflow to automatically run reviews before commits or pushes.
- **Support for Multiple Languages**: Although it’s optimized for Python, DevInspector can be configured to support other languages.
- **Detailed Reports**: Outputs detailed reports of any issues or recommendations, helping you understand and fix your code.

---

## Installation

To get started with **DevInspector**, follow the steps below to install dependencies and set up the tool.

### Prerequisites

- Python 3.10 or higher
- Git (for version control)
- A text editor or IDE (Visual Studio Code, PyCharm, etc.)
- **ngrok** for local testing (optional for local webhook testing)

### Steps

1. **Clone the repository**:

   First, clone the repository to your local machine:

   ```bash
   git clone https://github.com/M3Sachin/DevInspector.git
   ```

2. **Install dependencies**:

   Navigate to the project directory and install the required dependencies using `pip`:

   ```bash
   cd DevInspector
   pip install -r requirements.txt
   ```

3. **Set up the environment**:

   If the project uses environment variables or configuration files (e.g., for accessing the Gemini API), create a `.env` file in the project root and provide the necessary API keys and configurations. An example `.env.example` is included to help you get started.

---

## Usage

Once you've installed **DevInspector**, you're ready to start reviewing your code!

### Running DevInspector

To run the tool, simply execute the following command:

```bash
python devinspector.py
```

This will begin the AI-driven code review process and output any detected issues, suggestions, and improvements in your code.

### Switching AI Models

While **DevInspector** is configured to use the **Gemini API** by default, you can easily switch to another AI model. Modify the `devinspector.py` file or the configuration file to specify a different model.

For example, if you want to use another API, replace the relevant API setup and authentication details with those for the model you prefer.

---

## Configuration

You can customize **DevInspector** to match your project’s specific needs by adjusting configuration files.

1. **AI Model Selection**: 
   - By default, **DevInspector** uses the Gemini API model for analysis. However, you can switch to any model by editing the configuration file or the relevant parts of the code where the AI model is set up.
   
2. **Coding Standards**:
   - DevInspector allows you to define your own coding rules and standards. Modify the configuration file to set your own preferences for code style, error detection, and more.

3. **Environment Variables**:
   - Store sensitive data, such as API keys and model configurations, in a `.env` file for security purposes. The tool will automatically load these variables during runtime.

For example, in the `.env` file:

```plaintext
GEMINI_API_KEY=your_api_key_here
MODEL_TYPE=gemini  # Change to your preferred model type
```

---

## Setting Up GitHub App with Repository Permissions

To integrate **DevInspector** with your GitHub repository and automate code review processes, you'll need to set up a GitHub App. Follow these steps to configure it:

### 1. Create a GitHub App

1. Go to [GitHub Developer Settings](https://github.com/settings/apps).
2. Click **New GitHub App**.
3. Fill out the required details:
   - **App Name**: Choose a name for your app.
   - **Homepage URL**: You can set this to your project's URL or any appropriate URL.
   - **Webhook URL**: The URL where GitHub will send webhook events (e.g., for pull requests or issues).
   - **Repository Permissions**: Grant the necessary permissions, such as reading repositories and pull requests.
   
4. Save your changes and take note of your **App ID**, **Client ID**, and **Client Secret**.

### 2. Install the GitHub App

1. Install your newly created GitHub App to the desired repository.
2. Follow GitHub's instructions to install the app.

### 3. Use GitHub Authentication in Your App

Integrate your GitHub App’s authentication into the **DevInspector** code, where necessary, to interact with GitHub APIs. You can configure the API credentials in your `.env` file.

---

## Testing Locally with ngrok

To test **DevInspector** locally and expose your local server to GitHub for webhook notifications, you can use **ngrok**. This allows you to simulate the environment where GitHub sends webhooks to your local server.

### Steps to Set Up ngrok:

1. **Install ngrok** (if you haven't already):

   - Go to the [ngrok website](https://ngrok.com/) and download it for your operating system.
   - Install ngrok by following the installation instructions.

2. **Start your server** on port 5000:

   Make sure your application is running on port 5000:

   ```bash
   python devinspector.py
   ```

3. **Start ngrok** on port 5000:

   In a new terminal window, run the following command to expose your local server:

   ```bash
   ngrok http 5000
   ```

4. **Get the public URL**: ngrok will generate a public URL (e.g., `http://<random_subdomain>.ngrok.io`). Use this URL to set up the **Webhook URL** in your GitHub App settings.

5. **Test webhook functionality**: Trigger an event (e.g., a new pull request) on your GitHub repository, and GitHub will send a webhook request to your local server. You should see the interaction in your terminal logs and output.

---

## Contributing

We welcome contributions to **DevInspector**! If you'd like to contribute, please follow these steps:

1. **Fork the repository** and create your own branch.
2. Make your changes and improvements.
3. **Write tests** (if applicable).
4. Open a **pull request** with a description of the changes.

Before submitting your pull request, ensure your code adheres to the project’s standards and passes all tests.

If you encounter a bug or have an idea for an enhancement, please open an **issue** in the repository.

---

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- Special thanks to the Gemini API and other AI models that make **DevInspector** possible.

---

Feel free to reach out if you have any questions or suggestions!

---
Buy me a coffe:<script type="text/javascript" src="https://cdnjs.buymeacoffee.com/1.0.0/button.prod.min.js" data-name="bmc-button" data-slug="M3Sachin" data-color="#FFDD00" data-emoji=""  data-font="Cookie" data-text="Buy me a coffee" data-outline-color="#000000" data-font-color="#000000" data-coffee-color="#ffffff" ></script>
