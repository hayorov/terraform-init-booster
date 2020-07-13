# terraform-init-booster

_A Pre-terraform routine that speedups terraform modules download for bulky blueprints._

## Problem statement

- Terraform v0.12.x and older downloads module from git source for every usage (<https://github.com/hashicorp/terraform/issues/11435>). For bulky blueprints with hundreds of similar modules that make the process of `terraform init` slow.

## Quickstart

    (blueprint folder)>tf-init-booster
    (blueprint folder)>terraform init

## Settings with environment variables

- LOGLEVEL=INFO
- GIT_PATH=/usr/bin/git

## Indications for use

- Git as module source
- Many modules with the same source

## Performance

Based on a blueprint with 580 modules, 10 of them unique.

- Pure `terraform init` - 3m08s
- Boosted + `terraform init` - 39s (2.7s + 36.5s)

## Compatibility

Designed for terraform v0.12 and v0.11

## Requrements

- Python 3.6+
- (optional) gitpython * module

\* otherwise, system git will be used
