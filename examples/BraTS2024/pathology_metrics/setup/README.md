# How this MLCube was created

1. Create the basic MLCube structure needed for the metrics model, e.g.:

```
mlcube_template/
├── mlcube.yaml
└── workspace
    └── parameters.yaml
```

where `parameters.yaml` is the config file needed to run GaNDLF metrics generator.

2. Create a custom entrypoint.py so that the model's predictions file can be joined with
the labels file.  Save under `setup`:

```
setup/
├── entrypoint.py
└── mlcube_template
    ├── mlcube.yaml
    └── workspace
        └── parameters.yaml
```

3. Install GaNDLF from source:

```bash
git clone https://github.com/mlcommons/GaNDLF.git
cd GaNDLF
pip install torch==2.2.1 torchvision==0.17.1 torchaudio==2.2.1 --index-url https://download.pytorch.org/whl/cpu &&
    pip install mlcube_docker
```

> [!NOTE] You must be using pip v24.0 or less.
> Otherwise, you will not be able to install the latest versions of mlcube_docker and mlcube.

4. Go back to this `setup` folder and run:

```
gandlf deploy -t docker --mlcube-type metrics -r ./mlcube_template -o ../mlcube -e ./entrypoint.py
```

5. Push Docker image (and ensure image is publicly accessible).

6. (Optional) Test the generated MLCube:

```
cd ../mlcube
mlcube configure -Pdocker.build_strategy=always &&
    mlcube run --task evaluate
```
