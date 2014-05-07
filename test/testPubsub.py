import unittest
import pubsub

def args_for_call(*args, **kwargs):
    """ Return a comparable version of the arguments
    that were passed to this function.

    This is used both during recording, and to construct
    arg values to test against.
    """
    return (args, kwargs)

class RecordingCallback(object):
    """ Instances of this class can be used as 'callbacks' for testing
    They will record the arguments they were called with.
    This lets you use pop_call to check the order and arguments of each
    call. """

    def __init__(self):
        self.calls = []

    def reset(self):
        """ Clear all of the calls that have been made up to this point """
        self.calls = []

    def __call__(self, *args, **kwargs):
        self.calls.append(args_for_call(*args, **kwargs))

    def pop_call(self):
        """ Return the earliest calls arguments. This will also
        remove that call from the calls list. Successive calls
        to pop_call will return the arguments to each call that
        was made, in the order they were made """
        return self.calls.pop(0)

    def is_empty(self):
        """ Check if there are no remaining calls in the call
        queue."""
        return not self.calls


class TestPubsub(unittest.TestCase):
    """ Test suite for testing pubsub

    These tests should also walk you through the
    usages of this library. While also verifying that
    it works!
    """

    def test_basic_usage(self):
        """ Basic usage:
        Subscribe a callback to a channel.
        Publish something to that channel.
        Callback gets called with whatever you published.
        """

        test_cb = RecordingCallback()
        # Subscribe to channel 'foo'
        pubsub.sub("foo", test_cb)

        # Elsewhere, publish to channel foo
        # This is equivilant to calling test_cb("bar")
        # since test_cb is subscribed to foo
        pubsub.pub("foo", "bar")

        # Check that the call made to test_cb
        # is the same as just calling with foo("bar")
        self.assertEqual(args_for_call("bar"), test_cb.pop_call())

        # No other calls should be in the queue
        self.assertTrue(test_cb.is_empty())

    def test_multiple_subs_same_channel(self):
        """ Multiple subscribers for a channel
        Multiple callbacks can be tied to the same channel.
        When something is published, each of them are called.
        """

        # two different callbacks
        test_cb1 = RecordingCallback()
        test_cb2 = RecordingCallback()

        # subscribed to the same channel
        pubsub.sub("foo", test_cb1)
        pubsub.sub("foo", test_cb2)

        # publish to the channel
        pubsub.pub("foo", "bar")

        # Both are called
        self.assertEqual(args_for_call("bar"), test_cb1.pop_call())
        self.assertEqual(args_for_call("bar"), test_cb2.pop_call())

        # only once
        self.assertTrue(test_cb1.is_empty())
        self.assertTrue(test_cb2.is_empty())

    def test_sub_multiple_channels(self):
        """ A callback can be subscribed to multiple channels.
        When either of the channels are published to, the callback is called
        """
        test_cb = RecordingCallback()

        # Listen to multiple channels
        pubsub.sub("foo", test_cb)
        pubsub.sub("bar", test_cb)

        # when 'foo' is published to, test_cb is called
        pubsub.pub("foo", "foo arg")
        self.assertEqual(args_for_call("foo arg"), test_cb.pop_call())

        # when 'bar' is published to, test_cb is called
        pubsub.pub("bar", "bar arg")
        self.assertEqual(args_for_call("bar arg"), test_cb.pop_call())

        self.assertTrue(test_cb.is_empty())

    def test_not_called_unless_subbed(self):
        """ Your callback is /only/ called when a channel its subscribed
        to is published to.

        Other publishes do nothing
        """
        test_cb = RecordingCallback()
        pubsub.sub("foo", test_cb)

        pubsub.pub("bar", "bar arg")

        self.assertTrue(test_cb.is_empty())

    def test_unsubscribing_stops_calls(self):
        """ To stop being subscribed to a channel, unsub exists.
        After calling unsub with the channel and callback, that
        callback should see no more updates.
        """
        test_cb = RecordingCallback()
        pubsub.sub("foo", test_cb)

        pubsub.pub("foo", "foo arg")

        # we are listening to channel foo
        self.assertEqual(args_for_call("foo arg"), test_cb.pop_call())
        self.assertTrue(test_cb.is_empty())

        #unsubscribe
        pubsub.unsub("foo", test_cb)

        # New publishes don't call your callback
        pubsub.pub("foo", "foo arg")
        self.assertTrue(test_cb.is_empty())

if __name__ == "__main__":
    unittest.main()
