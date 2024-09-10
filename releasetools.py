#
# Copyright (C) 2009 The Android Open Source Project
# Copyright (C) 2019 The Mokee Open Source Project
# Copyright (C) 2020-2021 The LineageOS Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import common
import re

def FullOTA_Assertions(info):
  AddBasebandAssertion(info, info.input_zip)
  return

def IncrementalOTA_Assertions(info):
  AddBasebandAssertion(info, info.input_zip)
  return

def FullOTA_InstallEnd(info):
  OTA_InstallEnd(info)
  return

def IncrementalOTA_InstallEnd(info):
  OTA_InstallEnd(info)
  return

def AddImage(info, basename, dest):
  name = basename
  path = "IMAGES/" + name
  if path not in info.input_zip.namelist():
    return

  data = info.input_zip.read(path)
  common.ZipWriteStr(info.output_zip, name, data)
  info.script.Print("Patching {} image unconditionally...".format(dest.split('/')[-1]))
  info.script.AppendExtra('package_extract_file("%s", "%s");' % (name, dest))

def AddImageRadio(info, basename, dest):
  name = basename
  if ("RADIO/" + basename) in info.input_zip.namelist():
    data = info.input_zip.read("RADIO/" + basename)
    common.ZipWriteStr(info.output_zip, name, data)
    info.script.Print("Patching {} image unconditionally...".format(dest.split('/')[-1]))
    info.script.AppendExtra('package_extract_file("%s", "%s");' % (name, dest))

def OTA_InstallEnd(info):
  AddImage(info, "dtbo.img", "/dev/block/bootdevice/by-name/dtbo")
  AddImage(info, "vbmeta.img", "/dev/block/bootdevice/by-name/vbmeta")
  AddImage(info, "vbmeta_system.img", "/dev/block/bootdevice/by-name/vbmeta_system")

  AddImageRadio(info, "cmnlib64.mbn", "/dev/block/bootdevice/by-name/cmnlib64")
  AddImageRadio(info, "imagefv.elf", "/dev/block/bootdevice/by-name/imagefv")
  AddImageRadio(info, "cmnlib.mbn", "/dev/block/bootdevice/by-name/cmnlib")
  AddImageRadio(info, "hyp.mbn", "/dev/block/bootdevice/by-name/hyp")
  AddImageRadio(info, "km4.mbn", "/dev/block/bootdevice/by-name/keymaster")
  AddImageRadio(info, "tz.mbn", "/dev/block/bootdevice/by-name/tz")
  AddImageRadio(info, "aop.mbn", "/dev/block/bootdevice/by-name/aop")
  AddImageRadio(info, "xbl_config.elf", "/dev/block/bootdevice/by-name/xbl_config")
  AddImageRadio(info, "BTFM.bin", "/dev/block/bootdevice/by-name/bluetooth")
  AddImageRadio(info, "uefi_sec.mbn", "/dev/block/bootdevice/by-name/uefisecapp")
  AddImageRadio(info, "NON-HLOS.bin", "/dev/block/bootdevice/by-name/modem")
  AddImageRadio(info, "qupv3fw.elf", "/dev/block/bootdevice/by-name/qupfw")
  AddImageRadio(info, "abl.elf", "/dev/block/bootdevice/by-name/abl")
  AddImageRadio(info, "dspso.bin", "/dev/block/bootdevice/by-name/dsp")
  AddImageRadio(info, "devcfg.mbn", "/dev/block/bootdevice/by-name/devcfg")
  AddImageRadio(info, "storsec.mbn", "/dev/block/bootdevice/by-name/storsec")
  AddImageRadio(info, "xbl.elf", "/dev/block/bootdevice/by-name/xbl")
  AddImageRadio(info, "ffu.img", "/dev/block/bootdevice/by-name/ffu")

  return

def AddBasebandAssertion(info, input_zip):
  android_info = input_zip.open("OTA/android-info.txt")
  for line in android_info.readlines():
    m = re.search(r'require\s+version-baseband\s*-\s*(.+)', line.decode('utf-8'))
    if m:
      hwc, modem_version, firmware_version = re.split('[=,]', m.group(1).rstrip())
      if (len(hwc) and len(modem_version) and len(firmware_version)):
        cmd = 'assert(getprop("ro.boot.hwc") == "{0}" && (xiaomi.verify_baseband("{1}") == "1" || abort("ERROR: This package requires firmware from MIUI {2} or newer. Please upgrade firmware and retry!");) || true);'
        info.script.AppendExtra(cmd.format(hwc, modem_version, firmware_version))
  return
