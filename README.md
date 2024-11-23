# xBRL Forge

![xBRL Forge Image](images/High-quality.webp)

## Overview

**xBRL Forge** is an open-source software solution designed to streamline the process of creating final XBRL (eXtensible Business Reporting Language) and iXBRL (Inline XBRL) reports by integrating data from multiple software applications. With xBRL Forge, users can effortlessly generate XBRL taxonomies and compile comprehensive reports using a simple JSON structure for integration.

## Features

- **Multi-Source Integration**: Seamlessly gather data from various software solutions and compile them into a unified XBRL or iXBRL report.
- **XBRL Taxonomy Generation**: Create customizable XBRL taxonomies to meet your reporting needs.
- **Easy JSON Structure**: Integrate data using an intuitive and straightforward JSON format.
- **Open Source**: Contribute to the community and enhance the functionality of xBRL Forge.

## Getting Started

### Prerequisites

- Python 3
- lxml

### Installation

#### from github

1. Clone the repository:
   ```bash
   git clone https://github.com/antonheitz/xBRL-Forge.git
   cd xBRL-Forge
   ```

2. Install dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

#### Via PyPI as package

```bash
pip install xbrl-forge
```

### Usage

1. Prepare your data in the JSON structure according to [the documentation](docs/JSON_INPUT.md).

2. Pass the data to the generation function defined [here](src/xbrl_forge/__init__.py).

### Example

See the [example file](run_example.py)

## Documentation

For detailed documentation on how to use xBRL Forge, including API references and examples, please refer to the [docs](docs/) folder.

## Contributing

We welcome contributions from the community! To contribute:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature/YourFeature`
3. Make your changes and commit them: `git commit -m 'Add your feature'`
4. Push to the branch: `git push origin feature/YourFeature`
5. Create a pull request.

PLEASE NOTE: this project uses the **REBASE STRATEGY**

Please ensure your contributions align with the project guidelines.

## License

This project is licensed under the APACHE 2.0 License - see the [LICENSE](LICENSE.md) file for details.

## Support

If you encounter any issues or have questions, feel free to open an issue in the GitHub repository or reach out via [email](mailto:anton.j.heitz@gmail.com).

---

Thank you for using xBRL Forge! We look forward to your feedback and contributions!