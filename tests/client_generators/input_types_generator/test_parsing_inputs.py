import ast

import pytest
from graphql import build_ast_schema, parse

from ariadne_codegen.client_generators.constants import BASE_MODEL_CLASS_NAME
from ariadne_codegen.client_generators.input_types import InputTypesGenerator

from ...utils import compare_ast, filter_class_defs


@pytest.mark.parametrize(
    "schema_str, expected_class_defs",
    [
        (
            """
            input CustomInput {
                field1: CustomInput2!
                field2: Int!
            }

            input CustomInput2 {
                field: Int!
            }
            """,
            [
                ast.ClassDef(
                    name="CustomInput",
                    bases=[ast.Name(id=BASE_MODEL_CLASS_NAME)],
                    keywords=[],
                    decorator_list=[],
                    body=[
                        ast.AnnAssign(
                            target=ast.Name(id="field1"),
                            annotation=ast.Name(id='"CustomInput2"'),
                            simple=1,
                        ),
                        ast.AnnAssign(
                            target=ast.Name(id="field2"),
                            annotation=ast.Name(id="int"),
                            simple=1,
                        ),
                    ],
                ),
                ast.ClassDef(
                    name="CustomInput2",
                    bases=[ast.Name(id=BASE_MODEL_CLASS_NAME)],
                    keywords=[],
                    decorator_list=[],
                    body=[
                        ast.AnnAssign(
                            target=ast.Name(id="field"),
                            annotation=ast.Name(id="int"),
                            simple=1,
                        )
                    ],
                ),
            ],
        )
    ],
)
def test_generate_returns_module_with_parsed_input_types(
    schema_str, expected_class_defs, base_model_import, upload_import
):
    generator = InputTypesGenerator(
        schema=build_ast_schema(parse(schema_str)),
        enums_module="enums",
        scalars_module_name="scalars",
        base_model_import=base_model_import,
        upload_import=upload_import,
    )

    module = generator.generate()

    class_defs = filter_class_defs(module)
    assert compare_ast(class_defs, expected_class_defs)


def test_generate_returns_module_with_classes_in_the_same_order_as_declared(
    base_model_import, upload_import
):
    schema_str = """
    input BeforeInput {
        field: Boolean!
    }

    input TestInput {
        field: SecondInput = { nested: { val: 1.5 } }
    }

    input SecondInput {
        nested: NestedInput! = { val: 2.5 }
    }

    input NestedInput {
        val: Float! 
    }

    input AfterInput {
        field: Boolean!
    }
    """
    expected_order = [
        "BeforeInput",
        "TestInput",
        "SecondInput",
        "NestedInput",
        "AfterInput",
    ]
    generator = InputTypesGenerator(
        schema=build_ast_schema(parse(schema_str)),
        enums_module="enums",
        scalars_module_name="scalars",
        base_model_import=base_model_import,
        upload_import=upload_import,
    )

    module = generator.generate()

    generated_class_names = [c.name for c in filter_class_defs(module)]
    assert generated_class_names == expected_order
