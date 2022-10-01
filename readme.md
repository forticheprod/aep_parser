<a name="readme-top"></a>

<!-- PROJECT NAME -->
<br />
<div align="center">
  <!-- <a href="https://gitlab.com/delaunay.ben/aep-parser">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a> -->

  <h3 align="center">aep-parser</h3>

  <p align="center">
    An After Effects file parser in Python!
    <!-- <br />
    <a href="https://gitlab.com/delaunay.ben/aep-parser"><strong>Explore the docs »</strong></a>
    <br /> -->
    <br />
    <!-- <a href="https://gitlab.com/delaunay.ben/aep-parser">View Demo</a>
    · -->
    <a href="https://gitlab.com/delaunay.ben/aep-parser/-/issues">Report Bug</a>
    ·
    <a href="https://gitlab.com/delaunay.ben/aep-parser/-/issues">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project


This as a .aep (After Effects Project) parser in Python. After Effects files (.aep) are encoded in RIFX format. This parser uses [Kaitai Struct](https://kaitai.io/) to parse .aep files and return a Project object containing items, layers, effects and properties. It is based on the Go equivalent [aftereffects-aep-parser](https://github.com/boltframe/aftereffects-aep-parser).

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

* Kaitai Struct
  ```sh
  pip install kaitaistruct
  ```

### Installation

1. Clone the repo
   ```sh
   git clone https://gitlab.com/delaunay.ben/aep-parser.git
   ```
2. Add the complete path to the `src/aep_parser` subfolder to your `PYTHONPATH` env var.

<p align="right">(<a href="#readme-top">back to top</a>)</p>




<!-- USAGE EXAMPLES -->
## Usage

```python
from aep_parser.project_parser import parse_project

aep__file_path = "01_empty.aep"
project = parse_project(aep__file_path)
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>




<!-- ROADMAP -->
## Roadmap

- [ ] Get an initial working version
- [ ] Add unit tests
- [ ] Add Changelog
- [ ] Ensure python 3 compatibility
- [ ] Multi-version Support
    - [ ] After Effects 2018
    - [ ] After Effects 2022

See the [open issues](https://gitlab.com/delaunay.ben/aep-parser/-/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>




<!-- CONTRIBUTING -->
## Contributing

Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a merge request. You can also simply open an issue with the tag "enhancement".

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Merge Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>




<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>




<!-- CONTACT -->
## Contact

Benoit Delaunay - benoit.delaunay@forticheprod.com

Project Link: [https://gitlab.com/delaunay.ben/aep-parser](https://gitlab.com/delaunay.ben/aep-parser)

<p align="right">(<a href="#readme-top">back to top</a>)</p>




<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* [aftereffects-aep-parser](https://github.com/boltframe/aftereffects-aep-parser)
* [Kaitai Struct](https://kaitai.io)

<p align="right">(<a href="#readme-top">back to top</a>)</p>
