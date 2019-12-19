from tests.utils import GIVEN, WHEN, THEN, lists_are_equal
from app.market.model.handler import ModelHandler
from infrastructure.third_party.adapter.stats_model import WeightedLinearRegression
from infrastructure.third_party.adapter.numpy_utils import (
    is_not_a_number,
    calculate_log,
)


def test_get_log_returns():
    GIVEN("an item with some compositional data and the model handler")
    item = get_model_data_item(id=16397186)
    handler = ModelHandler(wls_model=WeightedLinearRegression())
    y = item.get("compositional_sp_back_price_ts")
    WHEN("we get the log returns of the data")
    log_returns = handler._get_log_returns(y)
    THEN("the log returns have the correct length")
    assert len(log_returns) == len(y)
    THEN("the log returns are as expected")
    for i, cpit in enumerate(y):
        if i == 0:
            assert is_not_a_number(log_returns[i])
        else:
            lpit = y[i - 1]
            assert log_returns[i] == calculate_log(cpit / lpit)


def test_meets_wlr_criteria():
    GIVEN("model data and an instance of the model handler")
    handler = ModelHandler(wls_model=WeightedLinearRegression())
    model_data = get_model_data()
    WHEN(
        "we run the weighted linear regression component for each of the items in the model_data"
    )
    for item in model_data:
        result = handler._meets_wlr_criteria(item=item)
        if item.get("id") in [
            14554375,
            16397186,
            25887695,
        ]:  # these don't have that much movement, probably shouldn't bother!
            assert result
        else:
            assert not (result)


def test_get_results():
    GIVEN("model data and an instance of the model handler")
    handler = ModelHandler(wls_model=WeightedLinearRegression())
    model_data = get_model_data()
    WHEN("we get results")
    results = handler.get_results(items=model_data)
    THEN("the results are not empty")
    assert results
    THEN("there is only one result")
    assert len(results) == 1
    THEN("the result is as expected (from historical records)")
    result = results[0]
    original_item = get_model_data_item(id=16397186)
    assert result == {
        "id": original_item.get("id"),
        "buy_price": original_item.get("ex_offered_back_price_pit"),
        "returns_price": original_item.get("ex_offered_back_price_mc_pit"),
        "probability": original_item.get("compositional_sp_probability_pit"),
        "type": "BUY",
        "model_id": "SPMB",
    }


def get_model_data():
    return [
        {
            "id": 14554375,
            "combined_back_size_pit": 25180.289999999997,
            "compositional_sp_probability_pit": 0.10941023595912089,
            "compositional_ex_average_probability_pit": 0.11242339752790073,
            "ex_offered_back_price_mc_pit": 8.6,
            "ex_offered_back_price_pit": 9.0,
            "compositional_sp_back_price_ts": [
                8.522544664658614,
                8.522544664658614,
                8.522544664658614,
                8.522544664658614,
                8.522544664658614,
                8.522544664658614,
                8.522544664658614,
                8.981987699171906,
                8.981987699171906,
                8.981987699171906,
                8.981987699171906,
                8.981987699171906,
                8.981987699171906,
                8.981987699171906,
                8.981987699171906,
                8.981987699171906,
                8.981987699171906,
                8.981987699171906,
                8.981987699171906,
                9.119711571764531,
                9.119711571764531,
                9.119711571764531,
                9.119711571764531,
                9.119711571764531,
                9.119711571764531,
                9.119711571764531,
                9.119711571764531,
                9.119711571764531,
                9.119711571764531,
                9.119711571764531,
                9.119711571764531,
                9.6271345670104,
                9.6271345670104,
                9.6271345670104,
                9.6271345670104,
                9.6271345670104,
                9.6271345670104,
                9.6271345670104,
                9.6271345670104,
                9.6271345670104,
                9.6271345670104,
                9.6271345670104,
                9.6271345670104,
                9.139912652904172,
                9.139912652904172,
                9.139912652904172,
                9.139912652904172,
                9.139912652904172,
                9.139912652904172,
                9.139912652904172,
                9.139912652904172,
                9.139912652904172,
                9.139912652904172,
                9.139912652904172,
            ],
            "extract_time_ts": [
                -295.0,
                -290.0,
                -285.0,
                -280.0,
                -275.0,
                -272.0,
                -267.0,
                -262.0,
                -257.0,
                -252.0,
                -247.0,
                -242.0,
                -237.0,
                -232.0,
                -227.0,
                -222.0,
                -217.0,
                -212.0,
                -207.0,
                -202.0,
                -197.0,
                -192.0,
                -187.0,
                -182.0,
                -177.0,
                -172.0,
                -167.0,
                -162.0,
                -157.0,
                -152.0,
                -147.0,
                -142.0,
                -137.0,
                -132.0,
                -127.0,
                -122.0,
                -117.0,
                -112.0,
                -107.0,
                -102.0,
                -97.0,
                -92.0,
                -87.0,
                -82.0,
                -77.0,
                -72.0,
                -66.0,
                -62.0,
                -57.0,
                -52.0,
                -47.0,
                -42.0,
                -37.0,
                -33.0,
            ],
            "combined_back_size_ts": [
                12006.95,
                12046.95,
                12410.01,
                12568.12,
                12568.12,
                12568.12,
                12568.12,
                12593.12,
                12593.12,
                12612.54,
                12780.82,
                12780.82,
                12780.82,
                13056.24,
                14020.460000000001,
                14020.460000000001,
                14477.86,
                14497.86,
                14611.380000000001,
                14663.390000000001,
                14912.690000000002,
                14964.940000000002,
                15087.93,
                15127.93,
                15152.93,
                15515.800000000001,
                15528.75,
                15634.75,
                16127.83,
                16127.83,
                16244.53,
                16423.14,
                16873.17,
                16873.17,
                17212.39,
                17528.559999999994,
                17892.98999999999,
                18090.879999999994,
                18206.719999999994,
                18922.199999999997,
                19157.05,
                19669.839999999997,
                20277.519999999997,
                20664.349999999995,
                20709.669999999995,
                21058.969999999998,
                22270.399999999998,
                22386.16,
                22672.359999999997,
                23880.959999999995,
                24129.859999999993,
                24260.539999999997,
                24862.289999999997,
                25180.289999999997,
            ],
        },
        {
            "id": 16397186,
            "combined_back_size_pit": 53065.26,
            "compositional_sp_probability_pit": 0.19889500121124917,
            "compositional_ex_average_probability_pit": 0.15361551489380376,
            "ex_offered_back_price_mc_pit": 6.13,
            "ex_offered_back_price_pit": 6.4,
            "compositional_sp_back_price_ts": [
                5.896905347266066,
                5.896905347266066,
                5.896905347266066,
                5.896905347266066,
                5.896905347266066,
                5.896905347266066,
                5.896905347266066,
                6.508504554104934,
                6.508504554104934,
                6.508504554104934,
                6.508504554104934,
                6.508504554104934,
                6.508504554104934,
                6.508504554104934,
                6.508504554104934,
                6.508504554104934,
                6.508504554104934,
                6.508504554104934,
                6.508504554104934,
                6.523627081432984,
                6.523627081432984,
                6.523627081432984,
                6.523627081432984,
                6.523627081432984,
                6.523627081432984,
                6.523627081432984,
                6.523627081432984,
                6.523627081432984,
                6.523627081432984,
                6.523627081432984,
                6.523627081432984,
                5.258867744564055,
                5.258867744564055,
                5.258867744564055,
                5.258867744564055,
                5.258867744564055,
                5.258867744564055,
                5.258867744564055,
                5.258867744564055,
                5.258867744564055,
                5.258867744564055,
                5.258867744564055,
                5.258867744564055,
                5.027778445461713,
                5.027778445461713,
                5.027778445461713,
                5.027778445461713,
                5.027778445461713,
                5.027778445461713,
                5.027778445461713,
                5.027778445461713,
                5.027778445461713,
                5.027778445461713,
                5.027778445461713,
            ],
            "extract_time_ts": [
                -295.0,
                -290.0,
                -285.0,
                -280.0,
                -275.0,
                -272.0,
                -267.0,
                -262.0,
                -257.0,
                -252.0,
                -247.0,
                -242.0,
                -237.0,
                -232.0,
                -227.0,
                -222.0,
                -217.0,
                -212.0,
                -207.0,
                -202.0,
                -197.0,
                -192.0,
                -187.0,
                -182.0,
                -177.0,
                -172.0,
                -167.0,
                -162.0,
                -157.0,
                -152.0,
                -147.0,
                -142.0,
                -137.0,
                -132.0,
                -127.0,
                -122.0,
                -117.0,
                -112.0,
                -107.0,
                -102.0,
                -97.0,
                -92.0,
                -87.0,
                -82.0,
                -77.0,
                -72.0,
                -66.0,
                -62.0,
                -57.0,
                -52.0,
                -47.0,
                -42.0,
                -37.0,
                -33.0,
            ],
            "combined_back_size_ts": [
                21543.76,
                21543.76,
                21593.76,
                22484.6,
                22604.6,
                22710.239999999998,
                22913.8,
                22988.16,
                23058.16,
                23058.16,
                23108.16,
                23108.16,
                23290.19,
                23290.19,
                23380.19,
                23790.19,
                23800.19,
                24211.149999999998,
                24211.149999999998,
                24385.14,
                24816.64,
                24922.64,
                25368.12,
                25368.12,
                25424.12,
                25531.36,
                26731.359999999997,
                27614.139999999996,
                28972.729999999996,
                29325.519999999997,
                31502.819999999996,
                31812.829999999994,
                32824.42999999999,
                33070.44,
                33241.87999999999,
                33476.84,
                34010.95,
                36572.270000000004,
                37340.520000000004,
                39240.01000000001,
                39658.970000000016,
                39842.95000000001,
                40381.79000000001,
                43626.94000000002,
                43928.09000000001,
                44082.850000000006,
                46498.83,
                46782.83,
                47191.20000000001,
                47844.66,
                49368.0,
                51366.95000000001,
                52381.52000000001,
                53065.26,
            ],
        },
        {
            "id": 19431900,
            "combined_back_size_pit": 31737.340000000004,
            "compositional_sp_probability_pit": 0.1272450241632378,
            "compositional_ex_average_probability_pit": 0.1329281256034261,
            "ex_offered_back_price_mc_pit": 7.08,
            "ex_offered_back_price_pit": 7.4,
            "compositional_sp_back_price_ts": [
                7.585357164722829,
                7.585357164722829,
                7.585357164722829,
                7.585357164722829,
                7.585357164722829,
                7.585357164722829,
                7.585357164722829,
                7.728711765661997,
                7.728711765661997,
                7.728711765661997,
                7.728711765661997,
                7.728711765661997,
                7.728711765661997,
                7.728711765661997,
                7.728711765661997,
                7.728711765661997,
                7.728711765661997,
                7.728711765661997,
                7.728711765661997,
                7.534052696779073,
                7.534052696779073,
                7.534052696779073,
                7.534052696779073,
                7.534052696779073,
                7.534052696779073,
                7.534052696779073,
                7.534052696779073,
                7.534052696779073,
                7.534052696779073,
                7.534052696779073,
                7.534052696779073,
                7.801388580391108,
                7.801388580391108,
                7.801388580391108,
                7.801388580391108,
                7.801388580391108,
                7.801388580391108,
                7.801388580391108,
                7.801388580391108,
                7.801388580391108,
                7.801388580391108,
                7.801388580391108,
                7.801388580391108,
                7.8588534724716474,
                7.8588534724716474,
                7.8588534724716474,
                7.8588534724716474,
                7.8588534724716474,
                7.8588534724716474,
                7.8588534724716474,
                7.8588534724716474,
                7.8588534724716474,
                7.8588534724716474,
                7.8588534724716474,
            ],
            "extract_time_ts": [
                -295.0,
                -290.0,
                -285.0,
                -280.0,
                -275.0,
                -272.0,
                -267.0,
                -262.0,
                -257.0,
                -252.0,
                -247.0,
                -242.0,
                -237.0,
                -232.0,
                -227.0,
                -222.0,
                -217.0,
                -212.0,
                -207.0,
                -202.0,
                -197.0,
                -192.0,
                -187.0,
                -182.0,
                -177.0,
                -172.0,
                -167.0,
                -162.0,
                -157.0,
                -152.0,
                -147.0,
                -142.0,
                -137.0,
                -132.0,
                -127.0,
                -122.0,
                -117.0,
                -112.0,
                -107.0,
                -102.0,
                -97.0,
                -92.0,
                -87.0,
                -82.0,
                -77.0,
                -72.0,
                -66.0,
                -62.0,
                -57.0,
                -52.0,
                -47.0,
                -42.0,
                -37.0,
                -33.0,
            ],
            "combined_back_size_ts": [
                11322.730000000001,
                11322.730000000001,
                11322.730000000001,
                11432.73,
                12678.89,
                12678.89,
                12873.679999999998,
                12912.35,
                12912.35,
                12922.35,
                12952.35,
                13712.350000000002,
                13812.36,
                13916.370000000003,
                14460.36,
                15412.630000000001,
                15422.630000000001,
                16032.630000000001,
                16119.79,
                16415.280000000002,
                16612.46,
                16679.61,
                16798.07,
                16848.07,
                16898.32,
                18943.649999999998,
                19575.65,
                19593.54,
                19687.54,
                19782.54,
                20057.670000000002,
                21586.280000000002,
                21954.74,
                22476.730000000003,
                22986.450000000004,
                23651.660000000003,
                23953.99,
                23973.84,
                24345.17,
                24627.100000000002,
                25595.46,
                26213.17,
                26416.69,
                26609.989999999998,
                26638.07,
                27010.07,
                28279.329999999998,
                29233.33,
                29812.65,
                29854.42,
                30028.08,
                30636.04,
                31342.170000000006,
                31737.340000000004,
            ],
        },
        {
            "id": 20600580,
            "combined_back_size_pit": 24858.42,
            "compositional_sp_probability_pit": 0.10672396343251382,
            "compositional_ex_average_probability_pit": 0.10624493529438954,
            "ex_offered_back_price_mc_pit": 8.98,
            "ex_offered_back_price_pit": 9.4,
            "compositional_sp_back_price_ts": [
                9.491957887798765,
                9.491957887798765,
                9.491957887798765,
                9.491957887798765,
                9.491957887798765,
                9.491957887798765,
                9.491957887798765,
                9.211471818495797,
                9.211471818495797,
                9.211471818495797,
                9.211471818495797,
                9.211471818495797,
                9.211471818495797,
                9.211471818495797,
                9.211471818495797,
                9.211471818495797,
                9.211471818495797,
                9.211471818495797,
                9.211471818495797,
                9.416902996850181,
                9.416902996850181,
                9.416902996850181,
                9.416902996850181,
                9.416902996850181,
                9.416902996850181,
                9.416902996850181,
                9.416902996850181,
                9.416902996850181,
                9.416902996850181,
                9.416902996850181,
                9.416902996850181,
                9.898119275170037,
                9.898119275170037,
                9.898119275170037,
                9.898119275170037,
                9.898119275170037,
                9.898119275170037,
                9.898119275170037,
                9.898119275170037,
                9.898119275170037,
                9.898119275170037,
                9.898119275170037,
                9.898119275170037,
                9.369966855029173,
                9.369966855029173,
                9.369966855029173,
                9.369966855029173,
                9.369966855029173,
                9.369966855029173,
                9.369966855029173,
                9.369966855029173,
                9.369966855029173,
                9.369966855029173,
                9.369966855029173,
            ],
            "extract_time_ts": [
                -295.0,
                -290.0,
                -285.0,
                -280.0,
                -275.0,
                -272.0,
                -267.0,
                -262.0,
                -257.0,
                -252.0,
                -247.0,
                -242.0,
                -237.0,
                -232.0,
                -227.0,
                -222.0,
                -217.0,
                -212.0,
                -207.0,
                -202.0,
                -197.0,
                -192.0,
                -187.0,
                -182.0,
                -177.0,
                -172.0,
                -167.0,
                -162.0,
                -157.0,
                -152.0,
                -147.0,
                -142.0,
                -137.0,
                -132.0,
                -127.0,
                -122.0,
                -117.0,
                -112.0,
                -107.0,
                -102.0,
                -97.0,
                -92.0,
                -87.0,
                -82.0,
                -77.0,
                -72.0,
                -66.0,
                -62.0,
                -57.0,
                -52.0,
                -47.0,
                -42.0,
                -37.0,
                -33.0,
            ],
            "combined_back_size_ts": [
                8657.66,
                8698.630000000001,
                8698.630000000001,
                9239.61,
                9323.599999999999,
                9484.359999999999,
                9484.359999999999,
                9788.369999999999,
                9788.369999999999,
                12131.949999999999,
                12263.609999999999,
                12333.609999999999,
                12580.23,
                12580.23,
                12580.23,
                12680.23,
                13107.13,
                13131.59,
                13256.39,
                13294.169999999998,
                13764.019999999999,
                13786.239999999998,
                13996.239999999998,
                14016.239999999998,
                14265.8,
                14869.059999999998,
                14969.059999999998,
                15089.059999999998,
                15394.299999999997,
                15599.299999999997,
                15599.299999999997,
                15953.389999999998,
                16277.379999999997,
                16839.979999999996,
                18111.629999999997,
                18277.51,
                18709.489999999998,
                18914.73,
                18943.489999999998,
                19040.94,
                20093.15,
                20475.41,
                20534.420000000002,
                20905.94,
                22142.41,
                22336.8,
                22849.920000000002,
                23099.920000000002,
                23225.98,
                23560.81,
                23884.49,
                23994.49,
                24832.41,
                24858.42,
            ],
        },
        {
            "id": 22953710,
            "combined_back_size_pit": 356441.94000000006,
            "compositional_sp_probability_pit": 0.3625564460882883,
            "compositional_ex_average_probability_pit": 0.4002802936197602,
            "ex_offered_back_price_mc_pit": 2.406,
            "ex_offered_back_price_pit": 2.48,
            "compositional_sp_back_price_ts": [
                2.686776612316264,
                2.686776612316264,
                2.686776612316264,
                2.686776612316264,
                2.686776612316264,
                2.686776612316264,
                2.686776612316264,
                2.4913805801972746,
                2.4913805801972746,
                2.4913805801972746,
                2.4913805801972746,
                2.4913805801972746,
                2.4913805801972746,
                2.4913805801972746,
                2.4913805801972746,
                2.4913805801972746,
                2.4913805801972746,
                2.4913805801972746,
                2.4913805801972746,
                2.490082308320698,
                2.490082308320698,
                2.490082308320698,
                2.490082308320698,
                2.490082308320698,
                2.490082308320698,
                2.490082308320698,
                2.490082308320698,
                2.490082308320698,
                2.490082308320698,
                2.490082308320698,
                2.490082308320698,
                2.642989875171563,
                2.642989875171563,
                2.642989875171563,
                2.642989875171563,
                2.642989875171563,
                2.642989875171563,
                2.642989875171563,
                2.642989875171563,
                2.642989875171563,
                2.642989875171563,
                2.642989875171563,
                2.642989875171563,
                2.7581912024713637,
                2.7581912024713637,
                2.7581912024713637,
                2.7581912024713637,
                2.7581912024713637,
                2.7581912024713637,
                2.7581912024713637,
                2.7581912024713637,
                2.7581912024713637,
                2.7581912024713637,
                2.7581912024713637,
            ],
            "extract_time_ts": [
                -295.0,
                -290.0,
                -285.0,
                -280.0,
                -275.0,
                -272.0,
                -267.0,
                -262.0,
                -257.0,
                -252.0,
                -247.0,
                -242.0,
                -237.0,
                -232.0,
                -227.0,
                -222.0,
                -217.0,
                -212.0,
                -207.0,
                -202.0,
                -197.0,
                -192.0,
                -187.0,
                -182.0,
                -177.0,
                -172.0,
                -167.0,
                -162.0,
                -157.0,
                -152.0,
                -147.0,
                -142.0,
                -137.0,
                -132.0,
                -127.0,
                -122.0,
                -117.0,
                -112.0,
                -107.0,
                -102.0,
                -97.0,
                -92.0,
                -87.0,
                -82.0,
                -77.0,
                -72.0,
                -66.0,
                -62.0,
                -57.0,
                -52.0,
                -47.0,
                -42.0,
                -37.0,
                -33.0,
            ],
            "combined_back_size_ts": [
                152095.50999999998,
                152345.50999999998,
                154474.21999999997,
                154820.21999999997,
                158683.82999999996,
                158719.82999999996,
                161403.89999999994,
                161751.89999999994,
                163801.12999999995,
                164111.50999999995,
                165938.26999999996,
                169168.44999999995,
                170332.02999999997,
                170672.45999999996,
                171733.43999999997,
                172817.60999999996,
                181901.35999999996,
                182045.95999999993,
                184873.95999999993,
                185706.57999999993,
                188539.10999999993,
                189074.33999999994,
                193362.55999999994,
                195628.38999999996,
                196083.73999999996,
                197248.57999999996,
                207868.25999999995,
                213325.46999999994,
                223562.90999999997,
                227344.39999999997,
                230489.00999999995,
                245366.68999999997,
                252265.33999999997,
                253032.20999999996,
                265652.58999999997,
                266724.6099999999,
                268209.86999999994,
                270525.8899999999,
                275235.77,
                277676.58,
                283988.48000000004,
                289680.8,
                297368.22,
                299130.47,
                301607.73,
                304417.79,
                310756.41,
                313866.25999999995,
                318524.18000000005,
                320440.34,
                322231.58,
                334627.51000000007,
                349441.5300000001,
                356441.94000000006,
            ],
        },
        {
            "id": 25887695,
            "combined_back_size_pit": 35117.64000000001,
            "compositional_sp_probability_pit": 0.09516932914559002,
            "compositional_ex_average_probability_pit": 0.0945077330607197,
            "ex_offered_back_price_mc_pit": 10.025,
            "ex_offered_back_price_pit": 10.5,
            "compositional_sp_back_price_ts": [
                9.642719629348342,
                9.642719629348342,
                9.642719629348342,
                9.642719629348342,
                9.642719629348342,
                9.642719629348342,
                9.642719629348342,
                10.450509842084028,
                10.450509842084028,
                10.450509842084028,
                10.450509842084028,
                10.450509842084028,
                10.450509842084028,
                10.450509842084028,
                10.450509842084028,
                10.450509842084028,
                10.450509842084028,
                10.450509842084028,
                10.450509842084028,
                10.358123125377304,
                10.358123125377304,
                10.358123125377304,
                10.358123125377304,
                10.358123125377304,
                10.358123125377304,
                10.358123125377304,
                10.358123125377304,
                10.358123125377304,
                10.358123125377304,
                10.358123125377304,
                10.358123125377304,
                10.162503200449061,
                10.162503200449061,
                10.162503200449061,
                10.162503200449061,
                10.162503200449061,
                10.162503200449061,
                10.162503200449061,
                10.162503200449061,
                10.162503200449061,
                10.162503200449061,
                10.162503200449061,
                10.162503200449061,
                10.507586939802845,
                10.507586939802845,
                10.507586939802845,
                10.507586939802845,
                10.507586939802845,
                10.507586939802845,
                10.507586939802845,
                10.507586939802845,
                10.507586939802845,
                10.507586939802845,
                10.507586939802845,
            ],
            "extract_time_ts": [
                -295.0,
                -290.0,
                -285.0,
                -280.0,
                -275.0,
                -272.0,
                -267.0,
                -262.0,
                -257.0,
                -252.0,
                -247.0,
                -242.0,
                -237.0,
                -232.0,
                -227.0,
                -222.0,
                -217.0,
                -212.0,
                -207.0,
                -202.0,
                -197.0,
                -192.0,
                -187.0,
                -182.0,
                -177.0,
                -172.0,
                -167.0,
                -162.0,
                -157.0,
                -152.0,
                -147.0,
                -142.0,
                -137.0,
                -132.0,
                -127.0,
                -122.0,
                -117.0,
                -112.0,
                -107.0,
                -102.0,
                -97.0,
                -92.0,
                -87.0,
                -82.0,
                -77.0,
                -72.0,
                -66.0,
                -62.0,
                -57.0,
                -52.0,
                -47.0,
                -42.0,
                -37.0,
                -33.0,
            ],
            "combined_back_size_ts": [
                17709.11,
                18139.239999999998,
                18169.239999999998,
                18169.239999999998,
                18216.83,
                18216.83,
                18626.730000000007,
                18840.830000000005,
                18890.830000000005,
                18929.940000000006,
                18929.940000000006,
                19029.940000000006,
                19033.170000000006,
                19033.170000000006,
                19053.170000000006,
                19981.020000000004,
                19981.020000000004,
                20029.020000000004,
                20140.600000000006,
                20556.600000000006,
                20574.600000000006,
                20599.600000000006,
                21234.600000000006,
                21449.790000000005,
                21464.790000000005,
                21555.040000000005,
                21565.040000000005,
                22004.820000000003,
                22549.780000000006,
                22614.780000000006,
                22908.120000000006,
                22992.880000000005,
                23012.970000000005,
                23731.710000000006,
                24843.910000000007,
                25039.820000000007,
                25365.830000000005,
                25628.510000000006,
                25976.510000000006,
                26870.720000000005,
                28737.270000000004,
                28807.270000000004,
                30528.38,
                30826.170000000002,
                31603.230000000007,
                31908.350000000006,
                32250.840000000004,
                32724.620000000006,
                33894.09000000001,
                34069.20000000001,
                34089.41000000001,
                34271.030000000006,
                34481.94,
                35117.64000000001,
            ],
        },
    ]


def get_model_data_item(id):
    return next((item for item in get_model_data() if item.get("id") == id), None)
