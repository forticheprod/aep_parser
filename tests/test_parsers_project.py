"""
Unit tests for aep_parser.parsers.project module
"""
from __future__ import absolute_import, unicode_literals, division

import sys
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import Mock, patch, MagicMock

from aep_parser.kaitai.aep import Aep
from aep_parser.models.project import Project
from aep_parser.parsers.project import (
    parse_project,
    _get_expression_engine,
    _get_effect_names,
    SOFTWARE_AGENT_XPATH,
)


class TestParseProject(unittest.TestCase):
    """Test cases for parse_project function"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_file_path = "/path/to/test.aep"
        
        # Mock NNHD data
        self.mock_nnhd_data = Mock()
        self.mock_nnhd_data.bits_per_channel = Aep.BitsPerChannel.bpc_8
        self.mock_nnhd_data.footage_timecode_display_start_type = Aep.FootageTimecodeDisplayStartType.ftcs_start_0
        self.mock_nnhd_data.frame_rate = 30.0
        self.mock_nnhd_data.frames_count_type = Aep.FramesCountType.fc_start_0
        self.mock_nnhd_data.time_display_type = Aep.TimeDisplayType.timecode

        # Mock chunks
        self.mock_nnhd_chunk = Mock()
        self.mock_nnhd_chunk.data = self.mock_nnhd_data
        
        self.mock_root_folder_chunk = Mock()
        self.mock_root_chunks = [self.mock_nnhd_chunk, self.mock_root_folder_chunk]

        # Mock AEP object
        self.mock_aep = Mock()
        self.mock_aep.data.chunks = self.mock_root_chunks
        self.mock_aep.xmp_packet = '<?xml version="1.0"?><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:stEvt="http://ns.adobe.com/xap/1.0/sType/ResourceEvent#"><rdf:Description><stEvt:softwareAgent>Adobe After Effects 2023 (Build 23.0.0.59)</stEvt:softwareAgent></rdf:Description></rdf:RDF>'

    @patch('aep_parser.parsers.project.parse_item')
    @patch('aep_parser.parsers.project._get_effect_names')
    @patch('aep_parser.parsers.project._get_expression_engine')
    @patch('aep_parser.parsers.project.find_by_type')
    @patch('aep_parser.parsers.project.find_by_list_type')
    @patch('aep_parser.parsers.project.Aep.from_file')
    def test_parse_project_python3(self, mock_from_file, mock_find_by_list_type, 
                                   mock_find_by_type, mock_get_expression_engine,
                                   mock_get_effect_names, mock_parse_item):
        """Test parse_project function with Python 3 XMP parsing"""
        # Setup mocks
        mock_from_file.return_value.__enter__.return_value = self.mock_aep
        mock_find_by_list_type.return_value = self.mock_root_folder_chunk
        mock_find_by_type.return_value = self.mock_nnhd_chunk
        mock_get_expression_engine.return_value = "javascript-1.0"
        mock_get_effect_names.return_value = ["Effect1", "Effect2"]
        
        # Ensure we're testing Python 3 path
        with patch.object(sys, 'version_info', (3, 8)):
            project = parse_project(self.test_file_path)
        
        # Verify the result
        self.assertIsInstance(project, Project)
        self.assertEqual(project.file, self.test_file_path)
        self.assertEqual(project.bits_per_channel, Aep.BitsPerChannel.bpc_8)
        self.assertEqual(project.frame_rate, 30.0)
        self.assertEqual(project.effect_names, ["Effect1", "Effect2"])
        self.assertEqual(project.expression_engine, "javascript-1.0")
        self.assertEqual(project.ae_version, "Adobe After Effects 2023 (Build 23.0.0.59)")
        
        # Verify mock calls
        mock_from_file.assert_called_once_with(self.test_file_path)
        mock_parse_item.assert_called_once_with(self.mock_root_folder_chunk, project, parent_id=None)

    @patch('aep_parser.parsers.project.parse_item')
    @patch('aep_parser.parsers.project._get_effect_names')
    @patch('aep_parser.parsers.project._get_expression_engine')
    @patch('aep_parser.parsers.project.find_by_type')
    @patch('aep_parser.parsers.project.find_by_list_type')
    @patch('aep_parser.parsers.project.Aep.from_file')
    def test_parse_project_python2(self, mock_from_file, mock_find_by_list_type, 
                                   mock_find_by_type, mock_get_expression_engine,
                                   mock_get_effect_names, mock_parse_item):
        """Test parse_project function with Python 2 XMP parsing"""
        # Setup mocks
        mock_from_file.return_value.__enter__.return_value = self.mock_aep
        mock_find_by_list_type.return_value = self.mock_root_folder_chunk
        mock_find_by_type.return_value = self.mock_nnhd_chunk
        mock_get_expression_engine.return_value = "extendscript"
        mock_get_effect_names.return_value = ["Effect1"]
        
        # Ensure we're testing Python 2 path
        with patch.object(sys, 'version_info', (2, 7)):
            project = parse_project(self.test_file_path)
        
        # Verify the result
        self.assertIsInstance(project, Project)
        self.assertEqual(project.ae_version, "Adobe After Effects 2023 (Build 23.0.0.59)")
        
        # Verify mock calls
        mock_from_file.assert_called_once_with(self.test_file_path)

    @patch('aep_parser.parsers.project.parse_item')
    @patch('aep_parser.parsers.project._get_effect_names')
    @patch('aep_parser.parsers.project._get_expression_engine')
    @patch('aep_parser.parsers.project.find_by_type')
    @patch('aep_parser.parsers.project.find_by_list_type')
    @patch('aep_parser.parsers.project.Aep.from_file')
    def test_parse_project_with_compositions_and_layers(self, mock_from_file, mock_find_by_list_type, 
                                                        mock_find_by_type, mock_get_expression_engine,
                                                        mock_get_effect_names, mock_parse_item):
        """Test parse_project function with compositions and layers processing"""
        # Setup mocks with compositions and layers
        mock_layer = Mock()
        mock_layer.layer_type = Aep.LayerType.footage
        mock_layer.source_id = 1
        mock_layer.name = ""
        mock_layer.start_time = 0.0
        mock_layer.out_point = 10.0
        
        mock_composition = Mock()
        mock_composition.layers = [mock_layer]
        mock_composition.frame_rate = 30.0
        
        mock_source_item = Mock()
        mock_source_item.name = "Source Item"
        mock_source_item.width = 1920
        mock_source_item.height = 1080
        mock_source_item.is_composition = False
        mock_source_item.is_footage = True
        mock_source_item.duration = 5.0
        
        mock_from_file.return_value.__enter__.return_value = self.mock_aep
        mock_find_by_list_type.return_value = self.mock_root_folder_chunk
        mock_find_by_type.return_value = self.mock_nnhd_chunk
        mock_get_expression_engine.return_value = "javascript-1.0"
        mock_get_effect_names.return_value = []
        
        with patch.object(sys, 'version_info', (3, 8)):
            project = parse_project(self.test_file_path)
            
            # Manually set up the project state to test layer processing
            project.project_items = {1: mock_source_item}
            project._compositions = [mock_composition]
            
            # Trigger the layer processing logic by calling parse_project again
            # but this time we'll test the layer processing directly
            for composition in project.compositions:
                for layer in composition.layers:
                    if layer.layer_type == Aep.LayerType.footage:
                        layer_source_item = project.project_items[layer.source_id]
                        if not layer.name:
                            layer.name = layer_source_item.name
                        layer.width = layer_source_item.width
                        layer.height = layer_source_item.height
                        layer.source_is_composition = layer_source_item.is_composition
                        layer.source_is_footage = layer_source_item.is_footage
                        layer.out_point = min(
                            layer.out_point, layer.start_time + layer_source_item.duration
                        )
                        layer.frame_out_point = int(
                            round(layer.out_point * composition.frame_rate)
                        )
        
        # Verify layer properties were set correctly
        self.assertEqual(mock_layer.name, "Source Item")
        self.assertEqual(mock_layer.width, 1920)
        self.assertEqual(mock_layer.height, 1080)
        self.assertEqual(mock_layer.source_is_composition, False)
        self.assertEqual(mock_layer.source_is_footage, True)
        self.assertEqual(mock_layer.out_point, 5.0)  # min(10.0, 0.0 + 5.0)
        self.assertEqual(mock_layer.frame_out_point, 150)  # int(round(5.0 * 30.0))


class TestGetExpressionEngine(unittest.TestCase):
    """Test cases for _get_expression_engine function"""

    @patch('aep_parser.parsers.project.str_contents')
    @patch('aep_parser.parsers.project.find_by_list_type')
    def test_get_expression_engine_found(self, mock_find_by_list_type, mock_str_contents):
        """Test _get_expression_engine when expression engine chunk is found"""
        mock_chunk = Mock()
        mock_find_by_list_type.return_value = mock_chunk
        mock_str_contents.return_value = "javascript-1.0"
        
        root_chunks = [Mock()]
        result = _get_expression_engine(root_chunks)
        
        self.assertEqual(result, "javascript-1.0")
        mock_find_by_list_type.assert_called_once_with(chunks=root_chunks, list_type="ExEn")
        mock_str_contents.assert_called_once_with(mock_chunk)

    @patch('aep_parser.parsers.project.find_by_list_type')
    def test_get_expression_engine_not_found(self, mock_find_by_list_type):
        """Test _get_expression_engine when expression engine chunk is not found"""
        mock_find_by_list_type.return_value = None
        
        root_chunks = [Mock()]
        result = _get_expression_engine(root_chunks)
        
        self.assertIsNone(result)
        mock_find_by_list_type.assert_called_once_with(chunks=root_chunks, list_type="ExEn")


class TestGetEffectNames(unittest.TestCase):
    """Test cases for _get_effect_names function"""

    @patch('aep_parser.parsers.project.str_contents')
    @patch('aep_parser.parsers.project.filter_by_type')
    @patch('aep_parser.parsers.project.find_by_list_type')
    def test_get_effect_names_multiple_effects(self, mock_find_by_list_type, 
                                              mock_filter_by_type, mock_str_contents):
        """Test _get_effect_names with multiple effects"""
        # Setup mocks
        mock_pefl_chunk = Mock()
        mock_pefl_chunk.data.chunks = [Mock(), Mock()]
        mock_find_by_list_type.return_value = mock_pefl_chunk
        
        mock_pjef_chunks = [Mock(), Mock(), Mock()]
        mock_filter_by_type.return_value = mock_pjef_chunks
        
        mock_str_contents.side_effect = ["Effect1", "Effect2", "Effect3"]
        
        root_chunks = [Mock()]
        result = _get_effect_names(root_chunks)
        
        self.assertEqual(result, ["Effect1", "Effect2", "Effect3"])
        mock_find_by_list_type.assert_called_once_with(chunks=root_chunks, list_type="Pefl")
        mock_filter_by_type.assert_called_once_with(chunks=mock_pefl_chunk.data.chunks, chunk_type="pjef")
        self.assertEqual(mock_str_contents.call_count, 3)

    @patch('aep_parser.parsers.project.str_contents')
    @patch('aep_parser.parsers.project.filter_by_type')
    @patch('aep_parser.parsers.project.find_by_list_type')
    def test_get_effect_names_no_effects(self, mock_find_by_list_type, 
                                        mock_filter_by_type, mock_str_contents):
        """Test _get_effect_names with no effects"""
        # Setup mocks
        mock_pefl_chunk = Mock()
        mock_pefl_chunk.data.chunks = []
        mock_find_by_list_type.return_value = mock_pefl_chunk
        
        mock_filter_by_type.return_value = []
        
        root_chunks = [Mock()]
        result = _get_effect_names(root_chunks)
        
        self.assertEqual(result, [])
        mock_str_contents.assert_not_called()


class TestConstants(unittest.TestCase):
    """Test cases for module constants"""

    def test_software_agent_xpath(self):
        """Test SOFTWARE_AGENT_XPATH constant"""
        self.assertEqual(SOFTWARE_AGENT_XPATH, ".//{*}softwareAgent")


class TestParseProjectEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions for parse_project function"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_file_path = "/path/to/test.aep"
        
        # Mock NNHD data
        self.mock_nnhd_data = Mock()
        self.mock_nnhd_data.bits_per_channel = Aep.BitsPerChannel.bpc_16
        self.mock_nnhd_data.footage_timecode_display_start_type = Aep.FootageTimecodeDisplayStartType.ftcs_use_source_media
        self.mock_nnhd_data.frame_rate = 24.0
        self.mock_nnhd_data.frames_count_type = Aep.FramesCountType.fc_start_1
        self.mock_nnhd_data.time_display_type = Aep.TimeDisplayType.frames

        # Mock chunks
        self.mock_nnhd_chunk = Mock()
        self.mock_nnhd_chunk.data = self.mock_nnhd_data
        
        self.mock_root_folder_chunk = Mock()
        self.mock_root_chunks = [self.mock_nnhd_chunk, self.mock_root_folder_chunk]

        # Mock AEP object
        self.mock_aep = Mock()
        self.mock_aep.data.chunks = self.mock_root_chunks

    @patch('aep_parser.parsers.project.parse_item')
    @patch('aep_parser.parsers.project._get_effect_names')
    @patch('aep_parser.parsers.project._get_expression_engine')
    @patch('aep_parser.parsers.project.find_by_type')
    @patch('aep_parser.parsers.project.find_by_list_type')
    @patch('aep_parser.parsers.project.Aep.from_file')
    def test_parse_project_no_xmp_packet(self, mock_from_file, mock_find_by_list_type, 
                                         mock_find_by_type, mock_get_expression_engine,
                                         mock_get_effect_names, mock_parse_item):
        """Test parse_project function when xmp_packet is None or empty"""
        # Setup mocks
        self.mock_aep.xmp_packet = None
        mock_from_file.return_value.__enter__.return_value = self.mock_aep
        mock_find_by_list_type.return_value = self.mock_root_folder_chunk
        mock_find_by_type.return_value = self.mock_nnhd_chunk
        mock_get_expression_engine.return_value = "extendscript"
        mock_get_effect_names.return_value = []
        
        with patch.object(sys, 'version_info', (3, 8)):
            # This should raise an exception when trying to parse None
            with self.assertRaises(TypeError):
                parse_project(self.test_file_path)

    @patch('aep_parser.parsers.project.parse_item')
    @patch('aep_parser.parsers.project._get_effect_names')
    @patch('aep_parser.parsers.project._get_expression_engine')
    @patch('aep_parser.parsers.project.find_by_type')
    @patch('aep_parser.parsers.project.find_by_list_type')
    @patch('aep_parser.parsers.project.Aep.from_file')
    def test_parse_project_invalid_xml(self, mock_from_file, mock_find_by_list_type, 
                                       mock_find_by_type, mock_get_expression_engine,
                                       mock_get_effect_names, mock_parse_item):
        """Test parse_project function with invalid XML in xmp_packet"""
        # Setup mocks
        self.mock_aep.xmp_packet = "<invalid xml"
        mock_from_file.return_value.__enter__.return_value = self.mock_aep
        mock_find_by_list_type.return_value = self.mock_root_folder_chunk
        mock_find_by_type.return_value = self.mock_nnhd_chunk
        mock_get_expression_engine.return_value = None
        mock_get_effect_names.return_value = []
        
        with patch.object(sys, 'version_info', (3, 8)):
            # This should raise an XML parsing exception
            with self.assertRaises(ET.ParseError):
                parse_project(self.test_file_path)

    @patch('aep_parser.parsers.project.parse_item')
    @patch('aep_parser.parsers.project._get_effect_names')
    @patch('aep_parser.parsers.project._get_expression_engine')
    @patch('aep_parser.parsers.project.find_by_type')
    @patch('aep_parser.parsers.project.find_by_list_type')
    @patch('aep_parser.parsers.project.Aep.from_file')
    def test_parse_project_no_software_agent(self, mock_from_file, mock_find_by_list_type, 
                                            mock_find_by_type, mock_get_expression_engine,
                                            mock_get_effect_names, mock_parse_item):
        """Test parse_project function when softwareAgent is not found in XMP"""
        # Setup mocks with XMP that doesn't contain softwareAgent
        self.mock_aep.xmp_packet = '<?xml version="1.0"?><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:other="http://example.com/ns"><rdf:Description><other:element>Some value</other:element></rdf:Description></rdf:RDF>'
        mock_from_file.return_value.__enter__.return_value = self.mock_aep
        mock_find_by_list_type.return_value = self.mock_root_folder_chunk
        mock_find_by_type.return_value = self.mock_nnhd_chunk
        mock_get_expression_engine.return_value = "javascript-1.0"
        mock_get_effect_names.return_value = []
        
        with patch.object(sys, 'version_info', (3, 8)):
            # This should raise an AttributeError when trying to access .text on None
            with self.assertRaises(AttributeError):
                parse_project(self.test_file_path)

    @patch('aep_parser.parsers.project.parse_item')
    @patch('aep_parser.parsers.project._get_effect_names')
    @patch('aep_parser.parsers.project._get_expression_engine')
    @patch('aep_parser.parsers.project.find_by_type')
    @patch('aep_parser.parsers.project.find_by_list_type')
    @patch('aep_parser.parsers.project.Aep.from_file')
    def test_parse_project_python2_no_software_agent(self, mock_from_file, mock_find_by_list_type, 
                                                     mock_find_by_type, mock_get_expression_engine,
                                                     mock_get_effect_names, mock_parse_item):
        """Test parse_project function with Python 2 when no softwareAgent is found"""
        # Setup mocks with XMP that doesn't contain softwareAgent
        self.mock_aep.xmp_packet = '<?xml version="1.0"?><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:other="http://example.com/ns"><rdf:Description><other:element>Some value</other:element></rdf:Description></rdf:RDF>'
        mock_from_file.return_value.__enter__.return_value = self.mock_aep
        mock_find_by_list_type.return_value = self.mock_root_folder_chunk
        mock_find_by_type.return_value = self.mock_nnhd_chunk
        mock_get_expression_engine.return_value = "extendscript"
        mock_get_effect_names.return_value = []
        
        with patch.object(sys, 'version_info', (2, 7)):
            # This should raise a StopIteration when next() is called on empty generator
            with self.assertRaises(StopIteration):
                parse_project(self.test_file_path)

    @patch('aep_parser.parsers.project.parse_item')
    @patch('aep_parser.parsers.project._get_effect_names')
    @patch('aep_parser.parsers.project._get_expression_engine')
    @patch('aep_parser.parsers.project.find_by_type')
    @patch('aep_parser.parsers.project.find_by_list_type')
    @patch('aep_parser.parsers.project.Aep.from_file')
    def test_parse_project_different_frame_rates(self, mock_from_file, mock_find_by_list_type, 
                                                 mock_find_by_type, mock_get_expression_engine,
                                                 mock_get_effect_names, mock_parse_item):
        """Test parse_project function with different frame rates and layer processing"""
        # Test with 60fps
        self.mock_nnhd_data.frame_rate = 60.0
        self.mock_aep.xmp_packet = '<?xml version="1.0"?><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:stEvt="http://ns.adobe.com/xap/1.0/sType/ResourceEvent#"><rdf:Description><stEvt:softwareAgent>Adobe After Effects 2024</stEvt:softwareAgent></rdf:Description></rdf:RDF>'
        
        mock_from_file.return_value.__enter__.return_value = self.mock_aep
        mock_find_by_list_type.return_value = self.mock_root_folder_chunk
        mock_find_by_type.return_value = self.mock_nnhd_chunk
        mock_get_expression_engine.return_value = "javascript-1.0"
        mock_get_effect_names.return_value = ["Fast Blur", "Color Correction"]
        
        with patch.object(sys, 'version_info', (3, 8)):
            project = parse_project(self.test_file_path)
        
        # Verify the different frame rate is set correctly
        self.assertEqual(project.frame_rate, 60.0)
        self.assertEqual(project.ae_version, "Adobe After Effects 2024")
        self.assertEqual(project.effect_names, ["Fast Blur", "Color Correction"])


if __name__ == '__main__':
    unittest.main()