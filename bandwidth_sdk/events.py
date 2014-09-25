import json
from six import iteritems
from .utils import from_api
# Event abstraction


class Event(object):

    @staticmethod
    def create(data=None, **kwargs):
        """
        Factory method
        :param data: optional byte string of data
        :param kwargs: params dictionary
        :return: EventType instance or throw an error
        """
        if data is not None:
            api_data = json.loads(data.decode('utf-8'))
            event_as_dict = from_api(api_data)
        else:
            event_as_dict = from_api(kwargs)
        event_cls = _events.get(event_as_dict.get('event_type', ''))
        if not event_cls:
            raise ValueError('Unknown event {}'.format(event_as_dict))
        return event_cls(**event_as_dict)


class EventType(object):
    call_id = None
    _fields = frozenset(('call_id',))

    def __init__(self, **kwargs):
        from_ = kwargs.pop('from', None)
        if from_:
            kwargs['from_'] = from_
        for attr, val in iteritems(kwargs):
            if attr in self._fields:
                setattr(self, attr, val)


class CallEvent(EventType):
    @property
    def call(self):
        # avoid cyclic imports
        from .models import Call
        return Call(self.call_id)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.call_id)


class IncomingCallEvent(CallEvent):
    """
    Bandwidth API sends this message to the application when an incoming call arrives.
    For incoming call the callback set is the one related to the Application associated with the called number.
    """
    event_type = None
    from_ = None
    to = None
    call_uri = None
    call_state = None
    application_id = None
    time = None
    tag = None
    _fields = frozenset(('call_id', 'event_type', 'from_', 'to', 'call_uri', 'call_state', 'time',
                         'application_id', 'tag'))


class AnswerCallEvent(CallEvent):
    """
    Bandwidth API sends this message to the application when the call is answered.
    """
    event_type = None
    from_ = None
    to = None
    call_uri = None
    call_state = None
    application_id = None
    time = None
    tag = None
    _fields = frozenset(('call_id', 'event_type', 'from_', 'to', 'call_uri', 'call_state', 'time',
                         'application_id', 'tag'))


class HangupCallEvent(CallEvent):
    """
    Bandwidth API sends this message to the application when the call ends.
    """
    event_type = None
    from_ = None
    to = None
    call_uri = None
    call_state = None
    cause = None
    time = None
    tag = None
    _fields = frozenset(('call_id', 'event_type', 'from_', 'to', 'call_uri', 'call_state', 'time', 'cause', 'tag'))


class PlaybackCallEvent(CallEvent):
    """
    Bandwidth API sends this message to the application when audio file playback starts or stops.
    """
    event_type = None
    call_id = None
    call_uri = None
    status = None
    time = None
    tag = None
    _fields = frozenset(('call_id', 'event_type', 'from_', 'to', 'call_uri', 'tag', 'time'))

    @property
    def done(self):
        return self.status == 'done'


class GatherCallEvent(CallEvent):
    """
    Bandwidth API sends this message to the application when the gather dtmf is completed or an error occurs.
    """
    event_type = None
    call_id = None
    time = None
    reason = None
    gather_id = None
    state = None
    digits = None
    tag = None
    _fields = frozenset(('call_id', 'event_type', 'state', 'digits', 'tag', 'time', 'gather_id', 'reason'))

    @property
    def gather(self):
        return self.call.gather.get(self.gather_id)


class DtmfCallEvent(CallEvent):
    """
    Bandwidth API sends this message to the application when audio file playback starts or stops.
    """
    event_type = None
    call_id = None
    call_uri = None
    time = None
    dtmf_digit = None
    dtmf_duration = None
    tag = None
    _fields = frozenset(('event_type', 'call_id', 'call_uri', 'time', 'dtmf_digit', 'dtmf_duration', 'tag'))


class SpeakCallEvent(CallEvent):
    """
    Bandwidth API sends this message to the application when text-to-speech starts or stops.
    """
    event_type = None
    call_id = None
    call_uri = None
    status = None
    state = None
    time = None
    tag = None
    _fields = frozenset(('call_id', 'event_type', 'status', 'state', 'call_uri', 'tag', 'time'))

    @property
    def done(self):
        return self.status == 'done'


class ErrorCallEvent(CallEvent):
    """
    Bandwidth API sends this message to the application when an error occurs.
    """
    event_type = None
    from_ = None
    to = None
    call_id = None
    call_uri = None
    call_state = None
    time = None
    tag = None
    _fields = frozenset(('call_id', 'event_type', 'from_', 'to', 'call_uri', 'call_state', 'time', 'tag'))


class TimeoutCallEvent(CallEvent):
    """
    Bandwidth API sends this message to the application when the call is not answered until the specified timeout.
    """
    event_type = None
    from_ = None
    to = None
    call_id = None
    call_uri = None
    time = None
    tag = None
    _fields = frozenset(('call_id', 'event_type', 'from_', 'to', 'call_uri', 'time', 'tag'))


class RecordingCallEvent(CallEvent):
    """
    Bandwidth API sends this event to the application when an the recording media file is saved or an error occurs
    while saving it.
    """
    event_type = None
    call_id = None
    recording_id = None
    recording_uri = None
    state = None
    status = None
    start_time = None
    end_time = None
    tag = None
    _fields = frozenset(('call_id', 'event_type', 'recording_id', 'recording_uri', 'state', 'status', 'start_time',
                         'end_time', 'tag'))


class SmsEvent(EventType):
    """
    Bandwidth API sends this event to the application when an SMS is sent or received.
    """
    event_type = None
    direction = None
    message_id = None
    message_uri = None
    from_ = None
    to = None
    text = None
    application_id = None
    time = None
    state = None
    _fields = frozenset(('event_type', 'direction', 'message_id', 'message_uri', 'from_', 'to',
                         'text', 'application_id', 'time', 'state'))

    def __repr__(self):
        return 'Sms(message_id={})'.format(self.message_id)


class ConferenceEventMixin(EventType):
    conference_id = None

    @property
    def conference(self):
        from .models import Conference
        return Conference(self.conference_id)

    def __repr__(self):
        return '{}(conference_id={})'.format(self.__class__.__name__, self.conference_id)


class ConferenceEvent(ConferenceEventMixin):
    """
    Bandwidth API sends this event to the application when a conference is created or completed.
    """
    event_type = None
    conference_id = None
    conference_uri = None
    status = None
    created_time = None
    completed_time = None
    _fields = frozenset(('event_type', 'conference_id', 'conference_uri', 'status', 'created_time', 'completed_time'))


class ConferenceMemberEvent(ConferenceEventMixin, CallEvent):
    """
    Bandwidth API sends this message to the application when a conference member has joined / left the conference
    or when it as muted or put on hold.
    """
    event_type = None
    call_id = None
    conference_id = None
    active_members = None
    hold = None
    member_id = None
    member_uri = None
    mute = None
    state = None
    time = None
    _fields = frozenset(('event_type', 'conference_id', 'call_id', 'active_members', 'hold', 'member_id',
                         'member_uri', 'mute', 'state', 'time'))


class ConferencePlaybackEvent(ConferenceEventMixin):
    """
    Bandwidth API sends this message to the application when audio playback is started or ended / stopped
    in a conference.
    """
    event_type = None
    conference_id = None
    conference_uri = None
    status = None
    time = None
    _fields = frozenset(('event_type', 'conference_id', 'conference_uri', 'status', 'time'))


class ConferenceSpeakEvent(ConferenceEventMixin):
    """
    Bandwidth API sends this message to the application when speak is started or ended / stopped in a conference.
    """
    event_type = None
    conference_id = None
    conference_uri = None
    status = None
    time = None
    _fields = frozenset(('event_type', 'conference_id', 'conference_uri', 'status', 'time'))


_events = {'hangup': HangupCallEvent,
           'answer': AnswerCallEvent,
           'incomingcall': IncomingCallEvent,
           'gather': GatherCallEvent,
           'speak': SpeakCallEvent,
           'playback': PlaybackCallEvent,
           'error': ErrorCallEvent,
           'timeout': TimeoutCallEvent,
           'recording': RecordingCallEvent,
           'sms': SmsEvent,
           'conference': ConferenceEvent,
           'conference-member': ConferenceMemberEvent,
           'conference-speak': ConferenceSpeakEvent,
           'conference-playback': ConferencePlaybackEvent,
           'dtmf': DtmfCallEvent}
