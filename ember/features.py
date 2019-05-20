#!/usr/bin/python
''' Extracts some basic features from PE files. Many of the features
implemented have been used in previously published works. For more information,
check out the following resources:
* Schultz, et al., 2001: http://128.59.14.66/sites/default/files/binaryeval-ieeesp01.pdf
* Kolter and Maloof, 2006: http://www.jmlr.org/papers/volume7/kolter06a/kolter06a.pdf
* Shafiq et al., 2009: https://www.researchgate.net/profile/Fauzan_Mirza/publication/242084613_A_Framework_for_Efficient_Mining_of_Structural_Information_to_Detect_Zero-Day_Malicious_Portable_Executables/links/0c96052e191668c3d5000000.pdf
* Raman, 2012: http://2012.infosecsouthwest.com/files/speaker_materials/ISSW2012_Selecting_Features_to_Classify_Malware.pdf
* Saxe and Berlin, 2015: https://arxiv.org/pdf/1508.03096.pdf

It may be useful to do feature selection to reduce this set of features to a meaningful set
for your modeling problem.
'''

import re
import pefile
import hashlib
import numpy as np
from sklearn.feature_extraction import FeatureHasher
import time
import pandas as pd

class FeatureType(object):
    ''' Base class from which each feature type may inherit '''

    name = ''
    dim = 0

    def __repr__(self):
        return '{}({})'.format(self.name, self.dim)

    def raw_features(self, bytez, pe):
        ''' Generate a JSON-able representation of the file '''
        raise (NotImplemented)

    def process_raw_features(self, raw_obj):
        ''' Generate a feature vector from the raw features '''
        raise (NotImplemented)

    def feature_vector(self, bytez, pe):
        ''' Directly calculate the feature vector from the sample itself. This should only be implemented differently
        if there are significant speedups to be gained from combining the two functions. '''
        return self.process_raw_features(self.raw_features(bytez, pe))


# class ByteHistogram(FeatureType):
#     ''' Byte histogram (count + non-normalized) over the entire binary file '''

#     name = 'histogram'
#     dim = 256

#     def __init__(self):
#         super(FeatureType, self).__init__()

#     def raw_features(self, bytez, lief_binary):
#         counts = np.bincount(np.frombuffer(bytez, dtype=np.uint8), minlength=256)
#         return counts.tolist()

#     def process_raw_features(self, raw_obj):
#         counts = np.array(raw_obj, dtype=np.float32)
#         sum = counts.sum()
#         normalized = counts / sum
#         return normalized


# class ByteEntropyHistogram(FeatureType):
#     ''' 2d byte/entropy histogram based loosely on (Saxe and Berlin, 2015).
#     This roughly approximates the joint probability of byte value and local entropy.
#     See Section 2.1.1 in https://arxiv.org/pdf/1508.03096.pdf for more info.
#     '''

#     name = 'byteentropy'
#     dim = 256

#     def __init__(self, step=1024, window=2048):
#         super(FeatureType, self).__init__()
#         self.window = window
#         self.step = step

#     def _entropy_bin_counts(self, block):
#         # coarse histogram, 16 bytes per bin
#         c = np.bincount(block >> 4, minlength=16)  # 16-bin histogram
#         p = c.astype(np.float32) / self.window
#         wh = np.where(c)[0]
#         H = np.sum(-p[wh] * np.log2(
#             p[wh])) * 2  # * x2 b.c. we reduced information by half: 256 bins (8 bits) to 16 bins (4 bits)

#         Hbin = int(H * 2)  # up to 16 bins (max entropy is 8 bits)
#         if Hbin == 16:  # handle entropy = 8.0 bits
#             Hbin = 15

#         return Hbin, c

#     def raw_features(self, bytez, lief_binary):
#         output = np.zeros((16, 16), dtype=np.int)
#         a = np.frombuffer(bytez, dtype=np.uint8)
#         if a.shape[0] < self.window:
#             Hbin, c = self._entropy_bin_counts(a)
#             output[Hbin, :] += c
#         else:
#             # strided trick from here: http://www.rigtorp.se/2011/01/01/rolling-statistics-numpy.html
#             shape = a.shape[:-1] + (a.shape[-1] - self.window + 1, self.window)
#             strides = a.strides + (a.strides[-1],)
#             blocks = np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)[::self.step, :]

#             # from the blocks, compute histogram
#             for block in blocks:
#                 Hbin, c = self._entropy_bin_counts(block)
#                 output[Hbin, :] += c

#         return output.flatten().tolist()

#     def process_raw_features(self, raw_obj):
#         counts = np.array(raw_obj, dtype=np.float32)
#         sum = counts.sum()
#         normalized = counts / sum
#         return normalized


# class SectionInfo(FeatureType):
#     ''' Information about section names, sizes and entropy.  Uses hashing trick
#     to summarize all this section info into a feature vector.
#     '''

#     name = 'section'
#     dim = 5 + 50 + 50 + 50 + 50 + 50

#     def __init__(self):
#         super(FeatureType, self).__init__()

#     @staticmethod
#     def _properties(s):
#         return [str(c).split('.')[-1] for c in s.characteristics_lists]

#     def raw_features(self, bytez, lief_binary):
#         if lief_binary is None:
#             return {"entry": "", "sections": []}

#         # properties of entry point, or if invalid, the first executable section
#         try:
#             entry_section = lief_binary.section_from_offset(lief_binary.entrypoint).name
#         except lief.not_found:
#             # bad entry point, let's find the first executable section
#             entry_section = ""
#             for s in lief_binary.sections:
#                 if lief.PE.SECTION_CHARACTERISTICS.MEM_EXECUTE in s.characteristics_lists:
#                     entry_section = s.name
#                     break

#         raw_obj = {"entry": entry_section}
#         raw_obj["sections"] = [{
#             'name': s.name,
#             'size': s.size,
#             'entropy': s.entropy,
#             'vsize': s.virtual_size,
#             'props': self._properties(s)
#         } for s in lief_binary.sections]
#         return raw_obj

#     def process_raw_features(self, raw_obj):
#         sections = raw_obj['sections']
#         general = [
#             len(sections),  # total number of sections
#             # number of sections with nonzero size
#             sum(1 for s in sections if s['size'] == 0),
#             # number of sections with an empty name
#             sum(1 for s in sections if s['name'] == ""),
#             # number of RX
#             sum(1 for s in sections if 'MEM_READ' in s['props'] and 'MEM_EXECUTE' in s['props']),
#             # number of W
#             sum(1 for s in sections if 'MEM_WRITE' in s['props'])
#         ]
#         # gross characteristics of each section
#         section_sizes = [(s['name'], s['size']) for s in sections]
#         section_sizes_hashed = FeatureHasher(50, input_type="pair").transform([section_sizes]).toarray()[0]
#         section_entropy = [(s['name'], s['entropy']) for s in sections]
#         section_entropy_hashed = FeatureHasher(50, input_type="pair").transform([section_entropy]).toarray()[0]
#         section_vsize = [(s['name'], s['vsize']) for s in sections]
#         section_vsize_hashed = FeatureHasher(50, input_type="pair").transform([section_vsize]).toarray()[0]
#         entry_name_hashed = FeatureHasher(50, input_type="string").transform([raw_obj['entry']]).toarray()[0]
#         characteristics = [p for s in sections for p in s['props'] if s['name'] == raw_obj['entry']]
#         characteristics_hashed = FeatureHasher(50, input_type="string").transform([characteristics]).toarray()[0]

#         return np.hstack([
#             general, section_sizes_hashed, section_entropy_hashed, section_vsize_hashed, entry_name_hashed,
#             characteristics_hashed
#         ]).astype(np.float32)


# class ImportsInfo(FeatureType):
#     ''' Information about imported libraries and functions from the
#     import address table.  Note that the total number of imported
#     functions is contained in GeneralFileInfo.
#     '''

#     name = 'imports'
#     dim = 1280

#     def __init__(self):
#         super(FeatureType, self).__init__()

#     def raw_features(self, bytez, lief_binary):
#         imports = {}
#         if lief_binary is None:
#             return imports

#         for lib in lief_binary.imports:
#             if lib.name not in imports:
#                 imports[lib.name] = []  # libraries can be duplicated in listing, extend instead of overwrite

#             # Clipping assumes there are diminishing returns on the discriminatory power of imported functions
#             #  beyond the first 10000 characters, and this will help limit the dataset size
#             imports[lib.name].extend([entry.name[:10000] for entry in lib.entries])

#         return imports

#     def process_raw_features(self, raw_obj):
#         # unique libraries
#         libraries = list(set([l.lower() for l in raw_obj.keys()]))
#         libraries_hashed = FeatureHasher(256, input_type="string").transform([libraries]).toarray()[0]

#         # A string like "kernel32.dll:CreateFileMappingA" for each imported function
#         imports = [lib.lower() + ':' + e for lib, elist in raw_obj.items() for e in elist]
#         imports_hashed = FeatureHasher(1024, input_type="string").transform([imports]).toarray()[0]

#         # Two separate elements: libraries (alone) and fully-qualified names of imported functions
#         return np.hstack([libraries_hashed, imports_hashed]).astype(np.float32)


# class ExportsInfo(FeatureType):
#     ''' Information about exported functions. Note that the total number of exported
#     functions is contained in GeneralFileInfo.
#     '''

#     name = 'exports'
#     dim = 128

#     def __init__(self):
#         super(FeatureType, self).__init__()

#     def raw_features(self, bytez, lief_binary):
#         if lief_binary is None:
#             return []

#         # Clipping assumes there are diminishing returns on the discriminatory power of exports beyond
#         #  the first 10000 characters, and this will help limit the dataset size
#         clipped_exports = [export[:10000] for export in lief_binary.exported_functions]

#         return clipped_exports

#     def process_raw_features(self, raw_obj):
#         exports_hashed = FeatureHasher(128, input_type="string").transform([raw_obj]).toarray()[0]
#         return exports_hashed.astype(np.float32)


# class GeneralFileInfo(FeatureType):
#     ''' General information about the file '''

#     name = 'general'
#     dim = 10

#     def __init__(self):
#         super(FeatureType, self).__init__()

#     def raw_features(self, bytez, lief_binary):
#         if lief_binary is None:
#             return {
#                 'size': len(bytez),
#                 'vsize': 0,
#                 'has_debug': 0,
#                 'exports': 0,
#                 'imports': 0,
#                 'has_relocations': 0,
#                 'has_resources': 0,
#                 'has_signature': 0,
#                 'has_tls': 0,
#                 'symbols': 0
#             }

#         return {
#             'size': len(bytez),
#             'vsize': lief_binary.virtual_size,
#             'has_debug': int(lief_binary.has_debug),
#             'exports': len(lief_binary.exported_functions),
#             'imports': len(lief_binary.imported_functions),
#             'has_relocations': int(lief_binary.has_relocations),
#             'has_resources': int(lief_binary.has_resources),
#             'has_signature': int(lief_binary.has_signature),
#             'has_tls': int(lief_binary.has_tls),
#             'symbols': len(lief_binary.symbols),
#         }

#     def process_raw_features(self, raw_obj):
#         return np.asarray(
#             [
#                 raw_obj['size'], raw_obj['vsize'], raw_obj['has_debug'], raw_obj['exports'], raw_obj['imports'],
#                 raw_obj['has_relocations'], raw_obj['has_resources'], raw_obj['has_signature'], raw_obj['has_tls'],
#                 raw_obj['symbols']
#             ],
#             dtype=np.float32)


class HeaderFileInfo(FeatureType):
    '''
    DOS Header, Optiona Header, File Header 추출
    '''

    name = 'header'
    dim = 56

    def __init__(self):
        super(FeatureType, self).__init__()

    def raw_features(self, bytez, pe):
        raw_obj = {}

        pe_dict = pe.dump_dict()
        pe_dos_header = pe_dict['DOS_HEADER']
        
        # dos 헤더        
        dos_header = {}
        del pe_dos_header['Structure']

        for key, value in pe_dos_header.items():
            dos_header[key] = value['Value']

        dos_header['e_res'] = int.from_bytes(pe.DOS_HEADER.e_res, byteorder='little')
        dos_header['e_res2'] = int.from_bytes(pe.DOS_HEADER.e_res2, byteorder='little')
        
        # file 헤더
        file_header = {}
        
        pe_file_header = pe_dict['FILE_HEADER']
        del pe_file_header['Structure']

        for key, value in pe_file_header.items():
            file_header[key] = value['Value']

        file_header['TimeDateStamp'] = pe.FILE_HEADER.TimeDateStamp

        # optional 헤더
        optional_header = {}

        pe_optional_header = pe_dict['OPTIONAL_HEADER']
        del pe_optional_header['Structure']

        for key, value in pe_optional_header.items():
            optional_header[key] = value['Value']

        # 종합       
        raw_obj['dos_header'] = dos_header
        raw_obj['optional_header'] = optional_header
        raw_obj['file_header'] = file_header

        return raw_obj

    def process_raw_features(self, raw_obj):
        features = [
            list(raw_obj['dos_header'].values()) +
            list(raw_obj['optional_header'].values()) +
            list(raw_obj['file_header'].values())
        ]

        return np.hstack(features).astype(np.float32)
        # return np.hstack().astype(np.float32)


# class StringExtractor(FeatureType):
#     ''' Extracts strings from raw byte stream '''

#     name = 'strings'
#     dim = 1 + 1 + 1 + 96 + 1 + 1 + 1 + 1 + 1

#     def __init__(self):
#         super(FeatureType, self).__init__()
#         # all consecutive runs of 0x20 - 0x7f that are 5+ characters
#         self._allstrings = re.compile(b'[\x20-\x7f]{5,}')
#         # occurances of the string 'C:\'.  Not actually extracting the path
#         self._paths = re.compile(b'c:\\\\', re.IGNORECASE)
#         # occurances of http:// or https://.  Not actually extracting the URLs
#         self._urls = re.compile(b'https?://', re.IGNORECASE)
#         # occurances of the string prefix HKEY_.  No actually extracting registry names
#         self._registry = re.compile(b'HKEY_')
#         # crude evidence of an MZ header (dropper?) somewhere in the byte stream
#         self._mz = re.compile(b'MZ')

#     def raw_features(self, bytez, lief_binary):
#         allstrings = self._allstrings.findall(bytez)
#         if allstrings:
#             # statistics about strings:
#             string_lengths = [len(s) for s in allstrings]
#             avlength = sum(string_lengths) / len(string_lengths)
#             # map printable characters 0x20 - 0x7f to an int array consisting of 0-95, inclusive
#             as_shifted_string = [b - ord(b'\x20') for b in b''.join(allstrings)]
#             c = np.bincount(as_shifted_string, minlength=96)  # histogram count
#             # distribution of characters in printable strings
#             csum = c.sum()
#             p = c.astype(np.float32) / csum
#             wh = np.where(c)[0]
#             H = np.sum(-p[wh] * np.log2(p[wh]))  # entropy
#         else:
#             avlength = 0
#             c = np.zeros((96,), dtype=np.float32)
#             H = 0
#             csum = 0

#         return {
#             'numstrings': len(allstrings),
#             'avlength': avlength,
#             'printabledist': c.tolist(),  # store non-normalized histogram
#             'printables': int(csum),
#             'entropy': float(H),
#             'paths': len(self._paths.findall(bytez)),
#             'urls': len(self._urls.findall(bytez)),
#             'registry': len(self._registry.findall(bytez)),
#             'MZ': len(self._mz.findall(bytez))
#         }

#     def process_raw_features(self, raw_obj):
#         hist_divisor = float(raw_obj['printables']) if raw_obj['printables'] > 0 else 1.0
#         return np.hstack([
#             raw_obj['numstrings'], raw_obj['avlength'], raw_obj['printables'],
#             np.asarray(raw_obj['printabledist']) / hist_divisor, raw_obj['entropy'], raw_obj['paths'], raw_obj['urls'],
#             raw_obj['registry'], raw_obj['MZ']
#         ]).astype(np.float32)


# def GenerateTime(lief_binary):
#     fileheader = lief_binary.header
#     timestamp = time.gmtime(fileheader.time_date_stamps)
#     return time.strftime('%Y-%m', timestamp)


class PEFeatureExtractor(object):
    ''' Extract useful features from a PE file, and return as a vector of fixed size. '''

    # features = [
    #     ByteHistogram(), ByteEntropyHistogram(), StringExtractor(), GeneralFileInfo(), HeaderFileInfo(), SectionInfo(),
    #     ImportsInfo(), ExportsInfo()
    # ]
    features = [
        HeaderFileInfo(), 
    ]
    dim = sum([fe.dim for fe in features])

    def raw_features(self, filepath):
        try:
            pe = pefile.PE(filepath)
            bytez = open(filepath, 'rb').read()
        except pefile.PEFormatError as excp:
            print('PEFormatError : {}'.format(excp))
            pe = None
        except Exception as e:  # everything else (KeyboardInterrupt, SystemExit, ValueError):
            print(e)
            raise            
        
        features = {} #appeared
        features.update({fe.name: fe.raw_features(bytez, pe) for fe in self.features})

        return features

    def process_raw_features(self, raw_obj):
        feature_vectors = [fe.process_raw_features(raw_obj[fe.name]) for fe in self.features]
        return np.hstack(feature_vectors).astype(np.float32)

    def feature_vector(self, filepath):
        return self.process_raw_features(self.raw_features(filepath))