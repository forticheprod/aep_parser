from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import collections

from aep_parser.models.property_type_name import PropertyTypeName


def parse_property(propData interface{}, matchName string):
    prop = Property()

    # Apply some sensible default values
    prop.PropertyType = PropertyTypeCustom
    prop.SelectOptions = make([]string, 0)
    prop.MatchName = matchName
    prop.name = matchName
    switch matchName {
    case "ADBE Effect Parade":
        prop.name = "Effects"
    }

    # Handle different types of property data
    switch propData.(type) {
    case *rifx.List:
        propHead := propData.(*rifx.List)
        # Parse sub-properties
        prop.Properties = make([]*Property, 0)
        tdgpMap, orderedMatchNames := indexedGroupToMap(propHead)
        for idx, mn := range orderedMatchNames {
            subProp, err := parseProperty(tdgpMap[mn], mn)
            if err == nil {
                subProp.index = uint32(idx) + 1
                prop.Properties = append(prop.Properties, subProp)
            }
        }

        # Parse effect sub-properties
        if propHead.Identifier == "sspc" {
            prop.PropertyType = PropertyTypeGroup
            fnamBlock, err := propHead.FindByType("fnam")
            if err == nil {
                prop.name = fnamBlock.ToString()
            }
            tdgpBlock, err := propHead.SublistFind("tdgp")
            if err == nil {

                # Look for a tdsn which specifies the user-defined label of the property
                tdsnBlock, err := tdgpBlock.FindByType("tdsn")
                if err == nil {
                    label := fmt.Sprintf("%s", tdsnBlock.ToString())

                    # Check if there is a custom user defined label added. The default if there
                    # is not is "-_0_/-" for some unknown reason.
                    if label != "-_0_/-" {
                        prop.Label = label
                    }
                }
            }
            parTList := propHead.SublistMerge("parT")
            subPropMatchNames, subPropPards := pairMatchNames(parTList)
            for idx, mn := range subPropMatchNames {
                # Skip first pard entry (describes parent)
                if idx == 0 {
                    continue
                }
                subProp, err := parseProperty(subPropPards[idx], mn)
                if err == nil {
                    subProp.index = uint32(idx)
                    prop.Properties = append(prop.Properties, subProp)
                }
            }
        }
    case []interface{}:
        for _, entry := range propData.([]interface{}) {
            if block, ok := entry.(*rifx.Block); ok {
                switch block.Type {
                case "pdnm":
                    strContent := block.ToString()
                    if prop.PropertyType == PropertyTypeSelect {
                        prop.SelectOptions = strings.Split(strContent, "|")
                    } else if strContent != "" {
                        prop.name = strContent
                    }
                case "pard":
                    blockData := block.Data.([]byte)
                    prop.PropertyType = PropertyTypeName(binary.BigEndian.Uint16(blockData[14:16]))
                    if prop.PropertyType == 0x0a {
                        prop.PropertyType = PropertyTypeOneD
                    }
                    pardName := fmt.Sprintf("%s", bytes.Trim(blockData[16:48], "\x00"))
                    if pardName != "" {
                        prop.name = pardName
                    }
                }
            }
        }
    }

    return prop, nil
}

func pairMatchNames(head *rifx.List) ([]string, [][]interface{}) {
    matchNames := make([]string, 0)
    datum := make([][]interface{}, 0)
    if head != nil {
        groupIdx := -1
        skipToNextTDMNFlag := false
        for _, block := range head.Blocks {
            if block.Type == "tdmn" {
                matchName := fmt.Sprintf("%s", bytes.Trim(block.Data.([]byte), "\x00"))
                if matchName == "ADBE Group End" || matchName == "ADBE Effect Built In Params" {
                    skipToNextTDMNFlag = true
                    continue
                }
                matchNames = append(matchNames, matchName)
                skipToNextTDMNFlag = false
                groupIdx++
            } else if groupIdx >= 0 && !skipToNextTDMNFlag {
                if groupIdx >= len(datum) {
                    datum = append(datum, make([]interface{}, 0))
                }
                switch block.Data.(type) {
                case *rifx.List:
                    datum[groupIdx] = append(datum[groupIdx], block.Data)
                default:
                    datum[groupIdx] = append(datum[groupIdx], block)
                }
            }
        }
    }
    return matchNames, datum
}

func indexedGroupToMap(tdgpHead *rifx.List) (map[string]*rifx.List, []string) {
    tdgpMap := make(map[string]*rifx.List, 0)
    matchNames, contents := pairMatchNames(tdgpHead)
    for idx, matchName := range matchNames {
        tdgpMap[matchName] = contents[idx][0].(*rifx.List)
    }
    return tdgpMap, matchNames