from pathlib import Path
from dataclasses import dataclass
from enum import StrEnum
from typing import Optional, ClassVar, Literal, Union
import os

IS_RUNNING_GITHUB_ACTION = 'GITHUB_ACTIONS' in os.environ

def infer_source_root(path):
  path = Path(path)
  if not path.absolute():
    path = path.absolute()
  parts = path.parts
  for i, v in enumerate(parts):
    if v == 'build' and i > 0 and parts[i-1] == 'llvm-project':
      found_path = Path('/'.join(parts[:i]))
      assert found_path.parts[-1] == 'llvm-project'
      return found_path
  return None

def infer_build_include_root(path):
  path = Path(path).absolute()
  source_root = infer_source_root(path)
  if not source_root:
    return None
  if 'include/c++/v1' not in path:
    return None
  build_root = source_root / build
  if not path.is_relative_to(build_root):
    return None

  parts = path.parts[0:path.parts.index('v1') + 1]
  return Path(*parts)


def maybe_translate_build_path(xpath):
  path = Path(xpath).absolute()
  source_root = infer_source_root(path)
  if not source_root:
    return xpath
  build_include_root = infer_build_include_root(path)
  if not build_include_root:
    return xpath
  source_include_root = source_root / 'libcxx/include'
  rel_path = path.relative_to(build_include_root)
  result = source_include_root / rel_path
  if not result.exists():
    return xpath
  return str(result)


class Severity(StrEnum):
  NOTICE = "notice"
  WARNING = "warning"
  ERROR = "error"

@dataclass
class GithubAnnotation:
  NUM_EMITTED_ANNOTATIONS : ClassVar[int] = 0
  MAX_EMITTED_ANNOTATIONS : ClassVar[int] = 10

  message: str
  severity: Severity
  file : Optional[Union[str, Path]] = None
  line : Optional[int] = None
  endLine : Optional[int] = None
  title : Optional[str] = None


  def __str__(self):
    items = {k: getattr(self, k) for k in {'file', 'line', 'endLine', 'title'} if getattr(self,k) is not None}
    parts = ','.join([f'{k}={v}' for k,v in items.items()])
    if parts:
      parts = ' ' + parts
    assert '\n' not in parts
    message = self.message.replace('\n', '%0A')
    return f'::{self.severity.value}{parts}::{message}'

  def translate_path(self):
    if self.file is not None:
      self.file = maybe_translate_build_path(self.file)
    return self

  def emit(self, always=False):
    if not always:
      if not IS_RUNNING_GITHUB_ACTION:
        return
      self.NUM_EMITTED_ANNOTATIONS += 1

      if self.NUM_EMITTED_ANNOTATIONS == self.MAX_EMITTED_ANNOTATIONS:
        print('::notice::Max number of annotations created. No annotations will be emitted')
        return
      elif self.NUM_EMITTED_ANNOTATIONS > self.MAX_EMITTED_ANNOTATIONS:
        return

    print(str(self))


@dataclass
class Error(GithubAnnotation):
  severity : Literal[Severity.ERROR] = Severity.ERROR

@dataclass
class Warning(GithubAnnotation):
  severity : Literal[Severity.WARNING] = Severity.WARNING


@dataclass
class Notice(GithubAnnotation):
  severity : Literal[Severity.NOTICE] = Severity.NOTICE


if __name__ == '__main__':
  this_file =  Path(__file__)
  Error(file=this_file, line=44, message="This is an error").emit(always=True)
  Notice(file=this_file, line=112, message="Hello there\nthis is multiple lines").emit(always=True)
