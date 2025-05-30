/***************************************************************************
 *   Copyright (c) 2015 Stefan Tröger <stefantroeger@gmx.net>              *
 *                                                                         *
 *   This file is part of the FreeCAD CAx development system.              *
 *                                                                         *
 *   This library is free software; you can redistribute it and/or         *
 *   modify it under the terms of the GNU Library General Public           *
 *   License as published by the Free Software Foundation; either          *
 *   version 2 of the License, or (at your option) any later version.      *
 *                                                                         *
 *   This library  is distributed in the hope that it will be useful,      *
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
 *   GNU Library General Public License for more details.                  *
 *                                                                         *
 *   You should have received a copy of the GNU Library General Public     *
 *   License along with this library; see the file COPYING.LIB. If not,    *
 *   write to the Free Software Foundation, Inc., 59 Temple Place,         *
 *   Suite 330, Boston, MA  02111-1307, USA                                *
 *                                                                         *
 ***************************************************************************/

#include "PreCompiled.h"

#ifndef _PreComp_
#include <vtkPointData.h>
#endif

#include <App/FeaturePythonPyImp.h>
#include <App/GroupExtension.h>
#include <Gui/Application.h>
#include <Gui/Selection/Selection.h>
#include <Mod/Fem/App/FemAnalysis.h>
#include <Mod/Fem/App/FemPostPipeline.h>

#include "ViewProviderAnalysis.h"
#include "ViewProviderFemPostFunction.h"
#include "ViewProviderFemPostPipeline.h"
#include "ViewProviderFemPostPipelinePy.h"
#include "TaskPostBoxes.h"


using namespace FemGui;

PROPERTY_SOURCE(FemGui::ViewProviderFemPostPipeline, FemGui::ViewProviderFemPostObject)

ViewProviderFemPostPipeline::ViewProviderFemPostPipeline()
{
    ViewProviderGroupExtension::initExtension(this);
    sPixmap = "FEM_PostPipelineFromResult";
}

ViewProviderFemPostPipeline::~ViewProviderFemPostPipeline() = default;


void ViewProviderFemPostPipeline::updateData(const App::Property* prop)
{
    FemGui::ViewProviderFemPostObject::updateData(prop);

    Fem::FemPostPipeline* pipeline = getObject<Fem::FemPostPipeline>();
    if ((prop == &pipeline->Data) || (prop == &pipeline->Group)) {

        updateFunctionSize();
    }
}

void ViewProviderFemPostPipeline::updateFunctionSize()
{
    // we need to get the bounding box and set the function provider size
    Fem::FemPostPipeline* obj = getObject<Fem::FemPostPipeline>();
    Fem::FemPostFunctionProvider* fp = obj->getFunctionProvider();
    if (!fp) {
        return;
    }

    FemGui::ViewProviderFemPostFunctionProvider* vp =
        static_cast<FemGui::ViewProviderFemPostFunctionProvider*>(
            Gui::Application::Instance->getViewProvider(fp));

    if (obj->Data.getValue() && obj->Data.getValue()->IsA("vtkDataSet")) {
        vtkBoundingBox box = obj->getBoundingBox();

        vp->SizeX.setValue(box.GetLength(0) * 1.2);
        vp->SizeY.setValue(box.GetLength(1) * 1.2);
        vp->SizeZ.setValue(box.GetLength(2) * 1.2);
    }
}

namespace
{
// Function to get the analysis container related to the object
ViewProviderFemAnalysis* getAnalyzeView(App::DocumentObject* obj)
{
    ViewProviderFemAnalysis* analyzeView = nullptr;
    App::DocumentObject* grp = App::GroupExtension::getGroupOfObject(obj);

    if (Fem::FemAnalysis* analyze = freecad_cast<Fem::FemAnalysis*>(grp)) {
        analyzeView = freecad_cast<ViewProviderFemAnalysis*>(
            Gui::Application::Instance->getViewProvider(analyze));
    }

    return analyzeView;
};
}  // namespace

bool ViewProviderFemPostPipeline::onDelete(const std::vector<std::string>& objs)
{
    ViewProviderFemAnalysis* analyzeView = getAnalyzeView(this->getObject());
    if (analyzeView) {
        analyzeView->removeView(this);
    }

    return ViewProviderFemPostObject::onDelete(objs);
}

void ViewProviderFemPostPipeline::onSelectionChanged(const Gui::SelectionChanges& sel)
{
    // If a FemPostObject is selected in the document tree we must refresh its
    // color bar.
    // But don't do this if the object is invisible because other objects with a
    // color bar might be visible and the color bar is then wrong.
    if (sel.Type == Gui::SelectionChanges::AddSelection) {
        if (this->getObject()->Visibility.getValue()) {
            updateMaterial();
        }
        else {
            return;  // purposely nothing should be done
        }

        // Access analysis object
        ViewProviderFemAnalysis* analyzeView = getAnalyzeView(this->getObject());
        if (analyzeView) {
            analyzeView->highlightView(this);
        }
    }
}

void ViewProviderFemPostPipeline::updateColorBars()
{
    // take all visible childs and update its shape coloring
    auto children = claimChildren();
    for (auto& child : children) {
        if (child->Visibility.getValue()) {
            auto vpObject = dynamic_cast<FemGui::ViewProviderFemPostObject*>(
                Gui::Application::Instance->getViewProvider(child));
            if (vpObject) {
                vpObject->updateMaterial();
            }
        }
    }

    // if pipeline is visible, update it
    if (this->isVisible()) {
        updateMaterial();
    }
}

void ViewProviderFemPostPipeline::transformField(char* FieldName, double FieldFactor)
{
    Fem::FemPostPipeline* obj = getObject<Fem::FemPostPipeline>();

    vtkDataSet* dset = obj->getDataSet();
    if (!dset) {
        return;
    }
    vtkDataArray* pdata = dset->GetPointData()->GetArray(FieldName);
    if (!pdata) {
        return;
    }

    auto strFieldName = std::string(FieldName);

    // for EigenModes, we need to step through all available modes
    if (strFieldName.find("EigenMode") != std::string::npos) {
        int modeCount;
        std::string testFieldName;
        // since a valid FieldName must have been passed
        // we assume the mode number was < 10 and we can strip the last char
        strFieldName.pop_back();
        for (modeCount = 1; pdata; ++modeCount) {
            testFieldName = strFieldName + std::to_string(modeCount);
            pdata = dset->GetPointData()->GetArray(testFieldName.c_str());
            if (pdata) {
                scaleField(dset, pdata, FieldFactor);
            }
        }
    }
    else {
        scaleField(dset, pdata, FieldFactor);
    }
}

void ViewProviderFemPostPipeline::scaleField(vtkDataSet* dset,
                                             vtkDataArray* pdata,
                                             double FieldFactor)
{
    // safe guard
    if (!dset || !pdata) {
        return;
    }

    // step through all mesh points and scale them
    for (int i = 0; i < dset->GetNumberOfPoints(); ++i) {
        double value = 0;
        if (pdata->GetNumberOfComponents() == 1) {
            value = pdata->GetComponent(i, 0);
            pdata->SetComponent(i, 0, value * FieldFactor);
        }
        // if field is a vector
        else {
            for (int j = 0; j < pdata->GetNumberOfComponents(); ++j) {
                value = pdata->GetComponent(i, j);
                pdata->SetComponent(i, j, value * FieldFactor);
            }
        }
    }
}

void ViewProviderFemPostPipeline::setupTaskDialog(TaskDlgPost* dlg)
{
    // add the function box
    assert(dlg->getView() == this);
    ViewProviderFemPostObject::setupTaskDialog(dlg);
    auto panel = new TaskPostFrames(this);
    dlg->addTaskBox(panel->windowIcon().pixmap(32), panel);
}


bool ViewProviderFemPostPipeline::acceptReorderingObjects() const
{
    return true;
}

bool ViewProviderFemPostPipeline::canDragObjectToTarget(App::DocumentObject*,
                                                        App::DocumentObject* target) const
{

    // allow drag only to other post groups
    if (target) {
        return target->hasExtension(Fem::FemPostGroupExtension::getExtensionClassTypeId());
    }
    else {
        return false;
    }
}


PyObject* ViewProviderFemPostPipeline::getPyObject()
{
    if (!pyViewObject) {
        pyViewObject = new ViewProviderFemPostPipelinePy(this);
    }
    pyViewObject->IncRef();
    return pyViewObject;
}
