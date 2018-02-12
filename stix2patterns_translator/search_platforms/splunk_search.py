import logging

logger = logging.getLogger(__name__)

from stix2patterns_translator.pattern_objects import ObservationExpression, ComparisonExpression, \
    ComparisonExpressionOperators, ComparisonComparators, Pattern, \
    CombinedComparisonExpression, CombinedObservationExpression, ObservationOperators
from stix2patterns_translator.data_models import CarDataMapper

from .splunk import encoders
from .splunk import object_scopers

class SplunkSearchTranslator:
    """ The core translator class. Instances should not be re-used """

    implemented_operators = {
        ObservationOperators.And: '{expr1} OR {expr2}',
        ObservationOperators.Or: '{expr1} OR {expr2}',
        # FollowedBy could also be done with transactions, however the original event would not be returned, though a
        # all the fields in the original event would be present in the transaction result.
        # For [x FOLLOWEDBY y], first find the most recent y, get its timestamp, and look for x's that occur earlier.
        # Use makeresults to inject a dummy event since a subsearch that yields no result will cause eval to error.
        # Presumably, no one will be looking for results prior to epoch=0.
        ObservationOperators.FollowedBy: "latest=[search {expr2} | append [makeresults 1 | eval _time=0]"
                                         "| head 1 | return $_time] | where {expr1}"
    }


    def __init__(self, pattern:Pattern, data_model_mapper, object_scoper = object_scopers.default_object_scoper):
        self.dmm = data_model_mapper
        self.pattern = pattern
        self.object_scoper = object_scoper
        self._pattern_prefix = "|where"  # How should the final SPL query string start.  By default, use '|where'

    def translate(self, expression):
        """ This is the worker method for the translation. It can be passed any of the STIX2 AST classes and will turn
            them in to strings. It's called recursively and then the results are composed into the full query. """

        if isinstance(expression, Pattern):
            # Note: The following call to translate might alter the value of self._pattern_prefix.
            expr = self.translate(expression.expression)

            return "{prefix} {expr}".format(prefix=self._pattern_prefix, expr=expr)
        elif isinstance(expression, ObservationExpression):
            translator = _ObservationExpressionTranslator(expression, self.dmm, self.object_scoper)
            return translator.translate(expression.comparison_expression)
        elif isinstance(expression, CombinedObservationExpression):
            combined_expr_format_string = self.implemented_operators[expression.operator]
            if expression.operator == ObservationOperators.FollowedBy:
                self._pattern_prefix = "|eval"
            return combined_expr_format_string.format(expr1=self.translate(expression.expr1),
                                                      expr2=self.translate(expression.expr2))
        else:
            import ipdb; ipdb.set_trace()
            raise NotImplementedError("Comparison type not implemented")


class _ObservationExpressionTranslator:

    _comparators = {
        ComparisonComparators.GreaterThan: ">",
        ComparisonComparators.GreaterThanOrEqual: ">=",
        ComparisonComparators.LessThan: "<",
        ComparisonComparators.LessThanOrEqual: "<=",
        ComparisonComparators.Equal: "=",
        ComparisonComparators.NotEqual: "!=",
        ComparisonComparators.Like: encoders.like,
        ComparisonComparators.In: encoders.set,
        ComparisonComparators.Matches: encoders.matches,
        ComparisonExpressionOperators.And: 'AND',
        ComparisonExpressionOperators.Or: 'OR'
    }

    def __init__(self, expression:ObservationExpression, dmm, object_scoper):
        # Expression that we're converting
        self.expression = expression
        self.dmm = dmm
        self.object_scoper = object_scoper

    def translate(self, expression):
        if isinstance(expression, ComparisonExpression):
            stix_object, stix_path = expression.object_path.split(':')

            # These are the native objects and fields
            object_mapping = self.dmm.map_object(stix_object)
            field_mapping = self.dmm.map_field(stix_object, stix_path)

            # This scopes the query to the object
            object_scoping = self.object_scoper(object_mapping)

            # Returns the actual comparison (as a translated string)
            return self._build_comparison(expression, object_scoping, field_mapping)
        elif isinstance(expression, CombinedComparisonExpression):
            return "({} {} {})".format(
                self.translate(expression.expr1),
                self._comparators[expression.operator],
                self.translate(expression.expr2)
            )

    def _build_comparison(self, expression, object_scoping, field_mapping):
        if expression.comparator in self._comparators:
            comparator = self._comparators[expression.comparator]
            if isinstance(comparator, str):
                splunk_comparison = self._maybe_negate("{} {} {}".format(
                    field_mapping,
                    comparator,
                    encoders.simple(expression.value)
                ), expression.negated)

                return "({} AND {})".format(object_scoping, splunk_comparison)
            else:
                return "({} AND {})".format(
                    object_scoping,
                    self._maybe_negate(comparator(field_mapping, expression.value), expression.negated)
                )
        else:
            raise NotImplementedError("Haven't implemented comparator")

    def _maybe_negate(self, splunk_comparison, negated):
        if negated:
            return "NOT ({})".format(splunk_comparison)
        else:
            return splunk_comparison

def translate_pattern(pattern: Pattern, data_model_mapping):
    import ipdb; ipdb.set_trace()
    # CAR + Splunk = we want to override the default object scoper, I guess?
    if isinstance(data_model_mapping, CarDataMapper):
        x = SplunkSearchTranslator(pattern, data_model_mapping, object_scoper = object_scopers.car_object_scoper)
    else:
        x = SplunkSearchTranslator(pattern, data_model_mapping)
    return x.translate(pattern)
