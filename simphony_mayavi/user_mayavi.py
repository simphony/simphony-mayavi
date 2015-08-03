from mayavi.core.registry import registry
from mayavi.core.pipeline_info import PipelineInfo
from mayavi.core.metadata import SourceMetadata

cuds_reader_info = SourceMetadata(
    id="CUDSReader",
    class_name="simphony_mayavi.sources.cuds_file_source.CUDSFileSource",
    tooltip="Load a CUDS file",
    desc="Load a SimPhoNy CUDS file",
    help="Load a SimPhoNy CUDS file",
    menu_name="CUDS file",
    extensions=['cuds'],
    wildcard='CUDS files (*.cuds)|*.cuds',
    output_info=PipelineInfo(
        datasets=['unstructured_grid', 'image_data', 'poly_data'],
        attribute_types=['any'],
        attributes=['scalars', 'vectors']))

registry.sources.append(cuds_reader_info)
