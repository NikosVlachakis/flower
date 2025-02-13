# Copyright 2020 Flower Labs GmbH. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""ProtoBuf serialization and deserialization."""


from typing import Any, Dict, List, MutableMapping, OrderedDict, Type, TypeVar, cast

from google.protobuf.message import Message

# pylint: disable=E0611
from flwr.proto.recordset_pb2 import Array as ProtoArray
from flwr.proto.recordset_pb2 import BoolList, BytesList
from flwr.proto.recordset_pb2 import ConfigsRecord as ProtoConfigsRecord
from flwr.proto.recordset_pb2 import ConfigsRecordValue as ProtoConfigsRecordValue
from flwr.proto.recordset_pb2 import DoubleList
from flwr.proto.recordset_pb2 import MetricsRecord as ProtoMetricsRecord
from flwr.proto.recordset_pb2 import MetricsRecordValue as ProtoMetricsRecordValue
from flwr.proto.recordset_pb2 import ParametersRecord as ProtoParametersRecord
from flwr.proto.recordset_pb2 import RecordSet as ProtoRecordSet
from flwr.proto.recordset_pb2 import Sint64List, StringList
from flwr.proto.task_pb2 import Value
from flwr.proto.transport_pb2 import (
    ClientMessage,
    Code,
    Parameters,
    Reason,
    Scalar,
    ServerMessage,
    Status,
)

# pylint: enable=E0611
from . import typing
from .configsrecord import ConfigsRecord
from .metricsrecord import MetricsRecord
from .parametersrecord import Array, ParametersRecord
from .recordset import RecordSet

#  === ServerMessage message ===


def server_message_to_proto(server_message: typing.ServerMessage) -> ServerMessage:
    """Serialize `ServerMessage` to ProtoBuf."""
    if server_message.get_properties_ins is not None:
        return ServerMessage(
            get_properties_ins=get_properties_ins_to_proto(
                server_message.get_properties_ins,
            )
        )
    if server_message.get_parameters_ins is not None:
        return ServerMessage(
            get_parameters_ins=get_parameters_ins_to_proto(
                server_message.get_parameters_ins,
            )
        )
    if server_message.fit_ins is not None:
        return ServerMessage(
            fit_ins=fit_ins_to_proto(
                server_message.fit_ins,
            )
        )
    if server_message.evaluate_ins is not None:
        return ServerMessage(
            evaluate_ins=evaluate_ins_to_proto(
                server_message.evaluate_ins,
            )
        )
    raise ValueError(
        "No instruction set in ServerMessage, cannot serialize to ProtoBuf"
    )


def server_message_from_proto(
    server_message_proto: ServerMessage,
) -> typing.ServerMessage:
    """Deserialize `ServerMessage` from ProtoBuf."""
    field = server_message_proto.WhichOneof("msg")
    if field == "get_properties_ins":
        return typing.ServerMessage(
            get_properties_ins=get_properties_ins_from_proto(
                server_message_proto.get_properties_ins,
            )
        )
    if field == "get_parameters_ins":
        return typing.ServerMessage(
            get_parameters_ins=get_parameters_ins_from_proto(
                server_message_proto.get_parameters_ins,
            )
        )
    if field == "fit_ins":
        return typing.ServerMessage(
            fit_ins=fit_ins_from_proto(
                server_message_proto.fit_ins,
            )
        )
    if field == "evaluate_ins":
        return typing.ServerMessage(
            evaluate_ins=evaluate_ins_from_proto(
                server_message_proto.evaluate_ins,
            )
        )
    raise ValueError(
        "Unsupported instruction in ServerMessage, cannot deserialize from ProtoBuf"
    )


#  === ClientMessage message ===


def client_message_to_proto(client_message: typing.ClientMessage) -> ClientMessage:
    """Serialize `ClientMessage` to ProtoBuf."""
    if client_message.get_properties_res is not None:
        return ClientMessage(
            get_properties_res=get_properties_res_to_proto(
                client_message.get_properties_res,
            )
        )
    if client_message.get_parameters_res is not None:
        return ClientMessage(
            get_parameters_res=get_parameters_res_to_proto(
                client_message.get_parameters_res,
            )
        )
    if client_message.fit_res is not None:
        return ClientMessage(
            fit_res=fit_res_to_proto(
                client_message.fit_res,
            )
        )
    if client_message.evaluate_res is not None:
        return ClientMessage(
            evaluate_res=evaluate_res_to_proto(
                client_message.evaluate_res,
            )
        )
    raise ValueError(
        "No instruction set in ClientMessage, cannot serialize to ProtoBuf"
    )


def client_message_from_proto(
    client_message_proto: ClientMessage,
) -> typing.ClientMessage:
    """Deserialize `ClientMessage` from ProtoBuf."""
    field = client_message_proto.WhichOneof("msg")
    if field == "get_properties_res":
        return typing.ClientMessage(
            get_properties_res=get_properties_res_from_proto(
                client_message_proto.get_properties_res,
            )
        )
    if field == "get_parameters_res":
        return typing.ClientMessage(
            get_parameters_res=get_parameters_res_from_proto(
                client_message_proto.get_parameters_res,
            )
        )
    if field == "fit_res":
        return typing.ClientMessage(
            fit_res=fit_res_from_proto(
                client_message_proto.fit_res,
            )
        )
    if field == "evaluate_res":
        return typing.ClientMessage(
            evaluate_res=evaluate_res_from_proto(
                client_message_proto.evaluate_res,
            )
        )
    raise ValueError(
        "Unsupported instruction in ClientMessage, cannot deserialize from ProtoBuf"
    )


#  === Parameters message ===


def parameters_to_proto(parameters: typing.Parameters) -> Parameters:
    """Serialize `Parameters` to ProtoBuf."""
    return Parameters(tensors=parameters.tensors, tensor_type=parameters.tensor_type)


def parameters_from_proto(msg: Parameters) -> typing.Parameters:
    """Deserialize `Parameters` from ProtoBuf."""
    tensors: List[bytes] = list(msg.tensors)
    return typing.Parameters(tensors=tensors, tensor_type=msg.tensor_type)


#  === ReconnectIns message ===


def reconnect_ins_to_proto(ins: typing.ReconnectIns) -> ServerMessage.ReconnectIns:
    """Serialize `ReconnectIns` to ProtoBuf."""
    if ins.seconds is not None:
        return ServerMessage.ReconnectIns(seconds=ins.seconds)
    return ServerMessage.ReconnectIns()


def reconnect_ins_from_proto(msg: ServerMessage.ReconnectIns) -> typing.ReconnectIns:
    """Deserialize `ReconnectIns` from ProtoBuf."""
    return typing.ReconnectIns(seconds=msg.seconds)


# === DisconnectRes message ===


def disconnect_res_to_proto(res: typing.DisconnectRes) -> ClientMessage.DisconnectRes:
    """Serialize `DisconnectRes` to ProtoBuf."""
    reason_proto = Reason.UNKNOWN
    if res.reason == "RECONNECT":
        reason_proto = Reason.RECONNECT
    elif res.reason == "POWER_DISCONNECTED":
        reason_proto = Reason.POWER_DISCONNECTED
    elif res.reason == "WIFI_UNAVAILABLE":
        reason_proto = Reason.WIFI_UNAVAILABLE
    return ClientMessage.DisconnectRes(reason=reason_proto)


def disconnect_res_from_proto(msg: ClientMessage.DisconnectRes) -> typing.DisconnectRes:
    """Deserialize `DisconnectRes` from ProtoBuf."""
    if msg.reason == Reason.RECONNECT:
        return typing.DisconnectRes(reason="RECONNECT")
    if msg.reason == Reason.POWER_DISCONNECTED:
        return typing.DisconnectRes(reason="POWER_DISCONNECTED")
    if msg.reason == Reason.WIFI_UNAVAILABLE:
        return typing.DisconnectRes(reason="WIFI_UNAVAILABLE")
    return typing.DisconnectRes(reason="UNKNOWN")


# === GetParameters messages ===


def get_parameters_ins_to_proto(
    ins: typing.GetParametersIns,
) -> ServerMessage.GetParametersIns:
    """Serialize `GetParametersIns` to ProtoBuf."""
    config = properties_to_proto(ins.config)
    return ServerMessage.GetParametersIns(config=config)


def get_parameters_ins_from_proto(
    msg: ServerMessage.GetParametersIns,
) -> typing.GetParametersIns:
    """Deserialize `GetParametersIns` from ProtoBuf."""
    config = properties_from_proto(msg.config)
    return typing.GetParametersIns(config=config)


def get_parameters_res_to_proto(
    res: typing.GetParametersRes,
) -> ClientMessage.GetParametersRes:
    """Serialize `GetParametersRes` to ProtoBuf."""
    status_msg = status_to_proto(res.status)
    if res.status.code == typing.Code.GET_PARAMETERS_NOT_IMPLEMENTED:
        return ClientMessage.GetParametersRes(status=status_msg)
    parameters_proto = parameters_to_proto(res.parameters)
    return ClientMessage.GetParametersRes(
        status=status_msg, parameters=parameters_proto
    )


def get_parameters_res_from_proto(
    msg: ClientMessage.GetParametersRes,
) -> typing.GetParametersRes:
    """Deserialize `GetParametersRes` from ProtoBuf."""
    status = status_from_proto(msg=msg.status)
    parameters = parameters_from_proto(msg.parameters)
    return typing.GetParametersRes(status=status, parameters=parameters)


# === Fit messages ===


def fit_ins_to_proto(ins: typing.FitIns) -> ServerMessage.FitIns:
    """Serialize `FitIns` to ProtoBuf."""
    parameters_proto = parameters_to_proto(ins.parameters)
    config_msg = metrics_to_proto(ins.config)
    return ServerMessage.FitIns(parameters=parameters_proto, config=config_msg)


def fit_ins_from_proto(msg: ServerMessage.FitIns) -> typing.FitIns:
    """Deserialize `FitIns` from ProtoBuf."""
    parameters = parameters_from_proto(msg.parameters)
    config = metrics_from_proto(msg.config)
    return typing.FitIns(parameters=parameters, config=config)


def fit_res_to_proto(res: typing.FitRes) -> ClientMessage.FitRes:
    """Serialize `FitIns` to ProtoBuf."""
    status_msg = status_to_proto(res.status)
    if res.status.code == typing.Code.FIT_NOT_IMPLEMENTED:
        return ClientMessage.FitRes(status=status_msg)
    parameters_proto = parameters_to_proto(res.parameters)
    metrics_msg = None if res.metrics is None else metrics_to_proto(res.metrics)
    return ClientMessage.FitRes(
        status=status_msg,
        parameters=parameters_proto,
        num_examples=res.num_examples,
        metrics=metrics_msg,
    )


def fit_res_from_proto(msg: ClientMessage.FitRes) -> typing.FitRes:
    """Deserialize `FitRes` from ProtoBuf."""
    status = status_from_proto(msg=msg.status)
    parameters = parameters_from_proto(msg.parameters)
    metrics = None if msg.metrics is None else metrics_from_proto(msg.metrics)
    return typing.FitRes(
        status=status,
        parameters=parameters,
        num_examples=msg.num_examples,
        metrics=metrics,
    )


# === GetProperties messages ===


def get_properties_ins_to_proto(
    ins: typing.GetPropertiesIns,
) -> ServerMessage.GetPropertiesIns:
    """Serialize `GetPropertiesIns` to ProtoBuf."""
    config = properties_to_proto(ins.config)
    return ServerMessage.GetPropertiesIns(config=config)


def get_properties_ins_from_proto(
    msg: ServerMessage.GetPropertiesIns,
) -> typing.GetPropertiesIns:
    """Deserialize `GetPropertiesIns` from ProtoBuf."""
    config = properties_from_proto(msg.config)
    return typing.GetPropertiesIns(config=config)


def get_properties_res_to_proto(
    res: typing.GetPropertiesRes,
) -> ClientMessage.GetPropertiesRes:
    """Serialize `GetPropertiesIns` to ProtoBuf."""
    status_msg = status_to_proto(res.status)
    if res.status.code == typing.Code.GET_PROPERTIES_NOT_IMPLEMENTED:
        return ClientMessage.GetPropertiesRes(status=status_msg)
    properties_msg = properties_to_proto(res.properties)
    return ClientMessage.GetPropertiesRes(status=status_msg, properties=properties_msg)


def get_properties_res_from_proto(
    msg: ClientMessage.GetPropertiesRes,
) -> typing.GetPropertiesRes:
    """Deserialize `GetPropertiesRes` from ProtoBuf."""
    status = status_from_proto(msg=msg.status)
    properties = properties_from_proto(msg.properties)
    return typing.GetPropertiesRes(status=status, properties=properties)


# === Evaluate messages ===


def evaluate_ins_to_proto(ins: typing.EvaluateIns) -> ServerMessage.EvaluateIns:
    """Serialize `EvaluateIns` to ProtoBuf."""
    parameters_proto = parameters_to_proto(ins.parameters)
    config_msg = metrics_to_proto(ins.config)
    return ServerMessage.EvaluateIns(parameters=parameters_proto, config=config_msg)


def evaluate_ins_from_proto(msg: ServerMessage.EvaluateIns) -> typing.EvaluateIns:
    """Deserialize `EvaluateIns` from ProtoBuf."""
    parameters = parameters_from_proto(msg.parameters)
    config = metrics_from_proto(msg.config)
    return typing.EvaluateIns(parameters=parameters, config=config)


def evaluate_res_to_proto(res: typing.EvaluateRes) -> ClientMessage.EvaluateRes:
    """Serialize `EvaluateIns` to ProtoBuf."""
    status_msg = status_to_proto(res.status)
    if res.status.code == typing.Code.EVALUATE_NOT_IMPLEMENTED:
        return ClientMessage.EvaluateRes(status=status_msg)
    metrics_msg = None if res.metrics is None else metrics_to_proto(res.metrics)
    return ClientMessage.EvaluateRes(
        status=status_msg,
        loss=res.loss,
        num_examples=res.num_examples,
        metrics=metrics_msg,
    )


def evaluate_res_from_proto(msg: ClientMessage.EvaluateRes) -> typing.EvaluateRes:
    """Deserialize `EvaluateRes` from ProtoBuf."""
    status = status_from_proto(msg=msg.status)
    metrics = None if msg.metrics is None else metrics_from_proto(msg.metrics)
    return typing.EvaluateRes(
        status=status,
        loss=msg.loss,
        num_examples=msg.num_examples,
        metrics=metrics,
    )


# === Status messages ===


def status_to_proto(status: typing.Status) -> Status:
    """Serialize `Status` to ProtoBuf."""
    code = Code.OK
    if status.code == typing.Code.GET_PROPERTIES_NOT_IMPLEMENTED:
        code = Code.GET_PROPERTIES_NOT_IMPLEMENTED
    if status.code == typing.Code.GET_PARAMETERS_NOT_IMPLEMENTED:
        code = Code.GET_PARAMETERS_NOT_IMPLEMENTED
    if status.code == typing.Code.FIT_NOT_IMPLEMENTED:
        code = Code.FIT_NOT_IMPLEMENTED
    if status.code == typing.Code.EVALUATE_NOT_IMPLEMENTED:
        code = Code.EVALUATE_NOT_IMPLEMENTED
    return Status(code=code, message=status.message)


def status_from_proto(msg: Status) -> typing.Status:
    """Deserialize `Status` from ProtoBuf."""
    code = typing.Code.OK
    if msg.code == Code.GET_PROPERTIES_NOT_IMPLEMENTED:
        code = typing.Code.GET_PROPERTIES_NOT_IMPLEMENTED
    if msg.code == Code.GET_PARAMETERS_NOT_IMPLEMENTED:
        code = typing.Code.GET_PARAMETERS_NOT_IMPLEMENTED
    if msg.code == Code.FIT_NOT_IMPLEMENTED:
        code = typing.Code.FIT_NOT_IMPLEMENTED
    if msg.code == Code.EVALUATE_NOT_IMPLEMENTED:
        code = typing.Code.EVALUATE_NOT_IMPLEMENTED
    return typing.Status(code=code, message=msg.message)


# === Properties messages ===


def properties_to_proto(properties: typing.Properties) -> Any:
    """Serialize `Properties` to ProtoBuf."""
    proto = {}
    for key in properties:
        proto[key] = scalar_to_proto(properties[key])
    return proto


def properties_from_proto(proto: Any) -> typing.Properties:
    """Deserialize `Properties` from ProtoBuf."""
    properties = {}
    for k in proto:
        properties[k] = scalar_from_proto(proto[k])
    return properties


# === Metrics messages ===


def metrics_to_proto(metrics: typing.Metrics) -> Any:
    """Serialize `Metrics` to ProtoBuf."""
    proto = {}
    for key in metrics:
        proto[key] = scalar_to_proto(metrics[key])
    return proto


def metrics_from_proto(proto: Any) -> typing.Metrics:
    """Deserialize `Metrics` from ProtoBuf."""
    metrics = {}
    for k in proto:
        metrics[k] = scalar_from_proto(proto[k])
    return metrics


# === Scalar messages ===


def scalar_to_proto(scalar: typing.Scalar) -> Scalar:
    """Serialize `Scalar` to ProtoBuf."""
    if isinstance(scalar, bool):
        return Scalar(bool=scalar)

    if isinstance(scalar, bytes):
        return Scalar(bytes=scalar)

    if isinstance(scalar, float):
        return Scalar(double=scalar)

    if isinstance(scalar, int):
        return Scalar(sint64=scalar)

    if isinstance(scalar, str):
        return Scalar(string=scalar)

    raise ValueError(
        f"Accepted types: {bool, bytes, float, int, str} (but not {type(scalar)})"
    )


def scalar_from_proto(scalar_msg: Scalar) -> typing.Scalar:
    """Deserialize `Scalar` from ProtoBuf."""
    scalar_field = scalar_msg.WhichOneof("scalar")
    scalar = getattr(scalar_msg, cast(str, scalar_field))
    return cast(typing.Scalar, scalar)


# === Value messages ===


_type_to_field = {
    float: "double",
    int: "sint64",
    bool: "bool",
    str: "string",
    bytes: "bytes",
}


_list_type_to_class_and_field = {
    float: (DoubleList, "double_list"),
    int: (Sint64List, "sint64_list"),
    bool: (BoolList, "bool_list"),
    str: (StringList, "string_list"),
    bytes: (BytesList, "bytes_list"),
}


def _check_value(value: typing.Value) -> None:
    if isinstance(value, tuple(_type_to_field.keys())):
        return
    if isinstance(value, list):
        if len(value) > 0 and isinstance(value[0], tuple(_type_to_field.keys())):
            data_type = type(value[0])
            for element in value:
                if isinstance(element, data_type):
                    continue
                raise TypeError(
                    f"Inconsistent type: the types of elements in the list must "
                    f"be the same (expected {data_type}, but got {type(element)})."
                )
    else:
        raise TypeError(
            f"Accepted types: {bool, bytes, float, int, str} or "
            f"list of these types."
        )


def value_to_proto(value: typing.Value) -> Value:
    """Serialize `Value` to ProtoBuf."""
    _check_value(value)

    arg = {}
    if isinstance(value, list):
        msg_class, field_name = _list_type_to_class_and_field[
            type(value[0]) if len(value) > 0 else int
        ]
        arg[field_name] = msg_class(vals=value)
    else:
        arg[_type_to_field[type(value)]] = value
    return Value(**arg)


def value_from_proto(value_msg: Value) -> typing.Value:
    """Deserialize `Value` from ProtoBuf."""
    value_field = cast(str, value_msg.WhichOneof("value"))
    if value_field.endswith("list"):
        value = list(getattr(value_msg, value_field).vals)
    else:
        value = getattr(value_msg, value_field)
    return cast(typing.Value, value)


# === Named Values ===


def named_values_to_proto(
    named_values: Dict[str, typing.Value],
) -> Dict[str, Value]:
    """Serialize named values to ProtoBuf."""
    return {name: value_to_proto(value) for name, value in named_values.items()}


def named_values_from_proto(
    named_values_proto: MutableMapping[str, Value]
) -> Dict[str, typing.Value]:
    """Deserialize named values from ProtoBuf."""
    return {name: value_from_proto(value) for name, value in named_values_proto.items()}


# === Record messages ===


T = TypeVar("T")


def _record_value_to_proto(
    value: Any, allowed_types: List[type], proto_class: Type[T]
) -> T:
    """Serialize `*RecordValue` to ProtoBuf."""
    arg = {}
    for t in allowed_types:
        # Single element
        # Note: `isinstance(False, int) == True`.
        if type(value) == t:  # pylint: disable=C0123
            arg[_type_to_field[t]] = value
            return proto_class(**arg)
        # List
        if isinstance(value, list) and all(isinstance(item, t) for item in value):
            list_class, field_name = _list_type_to_class_and_field[t]
            arg[field_name] = list_class(vals=value)
            return proto_class(**arg)
    # Invalid types
    raise TypeError(
        f"The type of the following value is not allowed "
        f"in '{proto_class.__name__}':\n{value}"
    )


def _record_value_from_proto(value_proto: Message) -> Any:
    """Deserialize `*RecordValue` from ProtoBuf."""
    value_field = cast(str, value_proto.WhichOneof("value"))
    if value_field.endswith("list"):
        value = list(getattr(value_proto, value_field).vals)
    else:
        value = getattr(value_proto, value_field)
    return value


def _record_value_dict_to_proto(
    value_dict: Dict[str, Any], allowed_types: List[type], value_proto_class: Type[T]
) -> Dict[str, T]:
    """Serialize the record value dict to ProtoBuf."""

    def proto(_v: Any) -> T:
        return _record_value_to_proto(_v, allowed_types, value_proto_class)

    return {k: proto(v) for k, v in value_dict.items()}


def _record_value_dict_from_proto(
    value_dict_proto: MutableMapping[str, Any]
) -> Dict[str, Any]:
    """Deserialize the record value dict from ProtoBuf."""
    return {k: _record_value_from_proto(v) for k, v in value_dict_proto.items()}


def array_to_proto(array: Array) -> ProtoArray:
    """Serialize Array to ProtoBuf."""
    return ProtoArray(**vars(array))


def array_from_proto(array_proto: ProtoArray) -> Array:
    """Deserialize Array from ProtoBuf."""
    return Array(
        dtype=array_proto.dtype,
        shape=list(array_proto.shape),
        stype=array_proto.stype,
        data=array_proto.data,
    )


def parameters_record_to_proto(record: ParametersRecord) -> ProtoParametersRecord:
    """Serialize ParametersRecord to ProtoBuf."""
    return ProtoParametersRecord(
        data_keys=record.data.keys(),
        data_values=map(array_to_proto, record.data.values()),
    )


def parameters_record_from_proto(
    record_proto: ProtoParametersRecord,
) -> ParametersRecord:
    """Deserialize ParametersRecord from ProtoBuf."""
    return ParametersRecord(
        array_dict=OrderedDict(
            zip(record_proto.data_keys, map(array_from_proto, record_proto.data_values))
        ),
        keep_input=False,
    )


def metrics_record_to_proto(record: MetricsRecord) -> ProtoMetricsRecord:
    """Serialize MetricsRecord to ProtoBuf."""
    return ProtoMetricsRecord(
        data=_record_value_dict_to_proto(
            record.data, [float, int], ProtoMetricsRecordValue
        )
    )


def metrics_record_from_proto(record_proto: ProtoMetricsRecord) -> MetricsRecord:
    """Deserialize MetricsRecord from ProtoBuf."""
    return MetricsRecord(
        metrics_dict=cast(
            Dict[str, typing.MetricsRecordValues],
            _record_value_dict_from_proto(record_proto.data),
        ),
        keep_input=False,
    )


def configs_record_to_proto(record: ConfigsRecord) -> ProtoConfigsRecord:
    """Serialize ConfigsRecord to ProtoBuf."""
    return ProtoConfigsRecord(
        data=_record_value_dict_to_proto(
            record.data, [int, float, bool, str, bytes], ProtoConfigsRecordValue
        )
    )


def configs_record_from_proto(record_proto: ProtoConfigsRecord) -> ConfigsRecord:
    """Deserialize ConfigsRecord from ProtoBuf."""
    return ConfigsRecord(
        configs_dict=cast(
            Dict[str, typing.ConfigsRecordValues],
            _record_value_dict_from_proto(record_proto.data),
        ),
        keep_input=False,
    )


# === RecordSet message ===


def recordset_to_proto(recordset: RecordSet) -> ProtoRecordSet:
    """Serialize RecordSet to ProtoBuf."""
    return ProtoRecordSet(
        parameters={
            k: parameters_record_to_proto(v) for k, v in recordset.parameters.items()
        },
        metrics={k: metrics_record_to_proto(v) for k, v in recordset.metrics.items()},
        configs={k: configs_record_to_proto(v) for k, v in recordset.configs.items()},
    )


def recordset_from_proto(recordset_proto: ProtoRecordSet) -> RecordSet:
    """Deserialize RecordSet from ProtoBuf."""
    return RecordSet(
        parameters={
            k: parameters_record_from_proto(v)
            for k, v in recordset_proto.parameters.items()
        },
        metrics={
            k: metrics_record_from_proto(v) for k, v in recordset_proto.metrics.items()
        },
        configs={
            k: configs_record_from_proto(v) for k, v in recordset_proto.configs.items()
        },
    )
